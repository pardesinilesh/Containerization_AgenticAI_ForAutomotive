"""
State management for build and deployment tracking using PostgreSQL + Argo DB.
"""
import os
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

Base = declarative_base()


class BuildJob(Base):
    """Database model for build jobs."""
    __tablename__ = "build_jobs"

    id = Column(String, primary_key=True)
    tool = Column(String, nullable=False)
    os = Column(String, nullable=False)
    version = Column(String, nullable=False)
    status = Column(String, default="pending")
    image_id = Column(String, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "tool": self.tool,
            "os": self.os,
            "version": self.version,
            "status": self.status,
            "image_id": self.image_id,
            "error": self.error,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "metadata": json.loads(self.metadata) if self.metadata else {},
        }


class Deployment(Base):
    """Database model for deployments."""
    __tablename__ = "deployments"

    id = Column(String, primary_key=True)
    image_id = Column(String, nullable=False)
    env = Column(String, nullable=False)
    replicas = Column(Integer, default=1)
    status = Column(String, default="pending")
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "image_id": self.image_id,
            "env": self.env,
            "replicas": self.replicas,
            "status": self.status,
            "error": self.error,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "metadata": json.loads(self.metadata) if self.metadata else {},
        }


class StateManager:
    """Manages state using PostgreSQL + Argo DB."""

    def __init__(self, db_url: Optional[str] = None):
        """
        Initialize state manager.

        Args:
            db_url: Database URL (default from env variable)
        """
        self.db_url = db_url or os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:postgres@localhost:5432/automotive"
        )
        self.engine = create_engine(self.db_url)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def init_db(self):
        """Initialize database tables."""
        Base.metadata.create_all(self.engine)

    def create_build_job(
        self,
        tool: str,
        os: str,
        version: str,
        status: str = "pending",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create a new build job.

        Args:
            tool: Tool name
            os: Target OS
            version: Tool version
            status: Initial status
            metadata: Additional metadata

        Returns:
            Build job ID
        """
        import uuid
        job_id = str(uuid.uuid4())

        with self.SessionLocal() as session:
            build_job = BuildJob(
                id=job_id,
                tool=tool,
                os=os,
                version=version,
                status=status,
                metadata=json.dumps(metadata or {}),
            )
            session.add(build_job)
            session.commit()

        return job_id

    def update_build_job(
        self,
        job_id: str,
        status: Optional[str] = None,
        image_id: Optional[str] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Update build job status."""
        with self.SessionLocal() as session:
            build_job = session.query(BuildJob).filter_by(id=job_id).first()
            if not build_job:
                return False

            if status:
                build_job.status = status
            if image_id:
                build_job.image_id = image_id
            if error:
                build_job.error = error
            if metadata:
                build_job.metadata = json.dumps(metadata)

            build_job.updated_at = datetime.utcnow()
            session.commit()

        return True

    def get_build_job(self, job_id: str) -> Dict[str, Any]:
        """Get build job details."""
        with self.SessionLocal() as session:
            build_job = session.query(BuildJob).filter_by(id=job_id).first()
            if not build_job:
                return {"error": "Build job not found"}
            return build_job.to_dict()

    def get_all_builds(self) -> List[Dict[str, Any]]:
        """Get all build jobs."""
        with self.SessionLocal() as session:
            builds = session.query(BuildJob).all()
            return [build.to_dict() for build in builds]

    def create_deployment(
        self,
        image_id: str,
        env: str,
        replicas: int = 1,
        status: str = "pending",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create a new deployment."""
        import uuid
        deployment_id = str(uuid.uuid4())

        with self.SessionLocal() as session:
            deployment = Deployment(
                id=deployment_id,
                image_id=image_id,
                env=env,
                replicas=replicas,
                status=status,
                metadata=json.dumps(metadata or {}),
            )
            session.add(deployment)
            session.commit()

        return deployment_id

    def update_deployment(
        self,
        deployment_id: str,
        status: Optional[str] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Update deployment status."""
        with self.SessionLocal() as session:
            deployment = session.query(Deployment).filter_by(id=deployment_id).first()
            if not deployment:
                return False

            if status:
                deployment.status = status
            if error:
                deployment.error = error
            if metadata:
                deployment.metadata = json.dumps(metadata)

            deployment.updated_at = datetime.utcnow()
            session.commit()

        return True

    def get_deployment(self, deployment_id: str) -> Dict[str, Any]:
        """Get deployment details."""
        with self.SessionLocal() as session:
            deployment = session.query(Deployment).filter_by(id=deployment_id).first()
            if not deployment:
                return {"error": "Deployment not found"}
            return deployment.to_dict()

    def get_all_images(self) -> Dict[str, Any]:
        """Get all built images from successful builds."""
        with self.SessionLocal() as session:
            builds = session.query(BuildJob).filter_by(status="completed").all()
            images = [
                {
                    "image_id": build.image_id,
                    "tool": build.tool,
                    "os": build.os,
                    "version": build.version,
                    "created_at": build.created_at.isoformat() if build.created_at else None,
                }
                for build in builds
                if build.image_id
            ]
            return {"images": images, "count": len(images)}

    def mark_resource_deleted(self, resource_type: str, resource_id: str) -> bool:
        """Mark a resource as deleted."""
        if resource_type == "build":
            return self.update_build_job(resource_id, status="deleted")
        elif resource_type == "deployment":
            return self.update_deployment(resource_id, status="deleted")
        return False
