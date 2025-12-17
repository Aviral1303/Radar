"""APScheduler configuration and job definitions."""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from sqlalchemy.orm import Session
from app.config import settings
from app.database import SessionLocal
from app.services.ingestion.factory import get_provider
from app.services.filters.profile_filter import ProfileFilter
from app.services.detection.founder_detector import FounderDetector
from app.services.notifications.factory import get_notifier
from app.models import Profile, Education, WorkHistory, TrackingMetadata
from app.schemas.profile import ProfileData


scheduler = AsyncIOScheduler()


def start_scheduler():
    """Start the scheduler with configured cron jobs."""
    if not settings.ENABLE_SCHEDULER:
        print("Scheduler is disabled in settings")
        return
    
    # Schedule daily ingestion job
    scheduler.add_job(
        run_ingestion_job,
        CronTrigger.from_crontab(settings.INGESTION_CRON),
        id="daily_ingestion",
        name="Daily Profile Ingestion",
        replace_existing=True,
    )
    
    # Schedule daily detection job
    scheduler.add_job(
        run_detection_job,
        CronTrigger.from_crontab(settings.DETECTION_CRON),
        id="daily_detection",
        name="Daily Founder Detection",
        replace_existing=True,
    )
    
    scheduler.start()
    print("Scheduler started")


async def run_ingestion_job():
    """
    Daily ingestion job.
    
    Fetches updated profiles from external API and stores them.
    """
    print(f"[{datetime.now()}] Starting ingestion job...")
    
    db: Session = SessionLocal()
    try:
        # Get tracking configuration
        config = db.query(TrackingMetadata).first()
        if not config:
            print("No tracking configuration found. Skipping ingestion.")
            return
        
        target_companies = config.target_companies or []
        target_states = config.target_states or []
        
        if not target_companies or not target_states:
            print("Target companies or states not configured. Skipping ingestion.")
            return
        
        # Initialize provider and filter
        provider = get_provider()
        profile_filter = ProfileFilter(
            target_companies=target_companies,
            target_states=target_states
        )
        
        # Fetch profiles for each company
        all_profiles = []
        for company in target_companies:
            try:
                print(f"Fetching profiles for company: {company}")
                profiles = await provider.search_by_company(
                    company,
                    filters={"state": target_states[0] if target_states else None}
                )
                all_profiles.extend(profiles)
            except Exception as e:
                print(f"Error fetching profiles for {company}: {e}")
                continue
        
        # Filter profiles
        filtered_profiles = profile_filter.filter(all_profiles)
        print(f"Filtered {len(filtered_profiles)} profiles from {len(all_profiles)} total")
        
        # Store or update profiles
        for profile_data in filtered_profiles:
            _store_profile(db, profile_data)
        
        # Update last ingestion timestamp
        config.last_ingestion = datetime.now()
        db.commit()
        
        print(f"[{datetime.now()}] Ingestion job completed. Processed {len(filtered_profiles)} profiles.")
    
    except Exception as e:
        print(f"Error in ingestion job: {e}")
        db.rollback()
    finally:
        db.close()


async def run_detection_job():
    """
    Daily detection job.
    
    Detects founder transitions and sends notifications.
    """
    print(f"[{datetime.now()}] Starting detection job...")
    
    db: Session = SessionLocal()
    try:
        # Run detection
        detector = FounderDetector(db)
        new_events = detector.detect_transitions()
        
        print(f"Detected {len(new_events)} new founder transitions")
        
        # Send notifications for new events
        if new_events:
            notifier = get_notifier()
            success = await notifier.send_founder_digest(new_events)
            
            if success:
                # Mark events as notified
                for event in new_events:
                    event.notified = True
                db.commit()
                print(f"Notifications sent for {len(new_events)} events")
            else:
                print("Failed to send notifications")
        
        # Update last detection timestamp
        config = db.query(TrackingMetadata).first()
        if config:
            config.last_detection = datetime.now()
            db.commit()
        
        print(f"[{datetime.now()}] Detection job completed.")
    
    except Exception as e:
        print(f"Error in detection job: {e}")
        db.rollback()
    finally:
        db.close()


def _store_profile(db: Session, profile_data: ProfileData):
    """
    Store or update a profile in the database.
    
    Args:
        db: Database session
        profile_data: Profile data to store
    """
    # Check if profile exists
    profile = db.query(Profile).filter(
        Profile.external_id == profile_data.external_id
    ).first()
    
    if not profile:
        # Create new profile
        profile = Profile(
            external_id=profile_data.external_id,
            full_name=profile_data.full_name,
            current_title=profile_data.current_title,
            current_company=profile_data.current_company,
            location_state=profile_data.location_state,
        )
        db.add(profile)
        db.flush()  # Get profile ID
    
    else:
        # Update existing profile
        profile.full_name = profile_data.full_name
        profile.current_title = profile_data.current_title
        profile.current_company = profile_data.current_company
        profile.location_state = profile_data.location_state
    
    # Store education
    for edu_data in profile_data.education:
        # Check if education already exists
        existing_edu = db.query(Education).filter(
            Education.profile_id == profile.id,
            Education.institution == edu_data.institution,
            Education.graduation_year == edu_data.graduation_year
        ).first()
        
        if not existing_edu:
            edu = Education(
                profile_id=profile.id,
                institution=edu_data.institution,
                graduation_year=edu_data.graduation_year,
                degree_type=edu_data.degree_type,
            )
            db.add(edu)
    
    # Store work history snapshot
    snapshot_date = datetime.now()
    for work_data in profile_data.work_history:
        # Create snapshot entry
        work = WorkHistory(
            profile_id=profile.id,
            title=work_data.title,
            company=work_data.company,
            start_date=work_data.start_date,
            end_date=work_data.end_date,
            is_current=work_data.is_current,
            snapshot_date=snapshot_date,
        )
        db.add(work)
    
    db.commit()

