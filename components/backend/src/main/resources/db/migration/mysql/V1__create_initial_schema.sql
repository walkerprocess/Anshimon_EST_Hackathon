CREATE TABLE elderly_profile (
    id BIGINT NOT NULL AUTO_INCREMENT,
    display_name VARCHAR(100) NOT NULL,
    phone_hash VARCHAR(128) NOT NULL,
    address VARCHAR(255) NOT NULL,
    latitude DECIMAL(10, 7) NOT NULL,
    longitude DECIMAL(10, 7) NOT NULL,
    region_code VARCHAR(20) NOT NULL,
    consent_status VARCHAR(30) NOT NULL,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    PRIMARY KEY (id),
    INDEX idx_elderly_region_code (region_code),
    INDEX idx_elderly_phone_hash (phone_hash)
);

CREATE TABLE risk_snapshot (
    id BIGINT NOT NULL AUTO_INCREMENT,
    region_code VARCHAR(20) NOT NULL,
    risk_score DECIMAL(5, 4) NOT NULL,
    risk_level VARCHAR(30) NOT NULL,
    target_start_at DATETIME(6) NOT NULL,
    target_end_at DATETIME(6) NOT NULL,
    model_version VARCHAR(100) NOT NULL,
    generated_at DATETIME(6) NOT NULL,
    PRIMARY KEY (id),
    INDEX idx_risk_region_target (region_code, target_start_at, target_end_at)
);

CREATE TABLE shelter (
    id BIGINT NOT NULL AUTO_INCREMENT,
    source_id VARCHAR(100) NOT NULL,
    name VARCHAR(150) NOT NULL,
    address VARCHAR(255) NOT NULL,
    latitude DECIMAL(10, 7) NOT NULL,
    longitude DECIMAL(10, 7) NOT NULL,
    open_status VARCHAR(30) NOT NULL,
    source_version VARCHAR(100) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uk_shelter_source_id (source_id)
);

CREATE TABLE intervention_plan (
    id BIGINT NOT NULL AUTO_INCREMENT,
    elderly_id BIGINT NOT NULL,
    risk_snapshot_id BIGINT NOT NULL,
    shelter_id BIGINT NULL,
    status VARCHAR(40) NOT NULL,
    guidance_json JSON NOT NULL,
    questions_json JSON NOT NULL,
    evidence_chunk_ids_json JSON NOT NULL,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    PRIMARY KEY (id),
    INDEX idx_plan_elderly_risk (elderly_id, risk_snapshot_id)
);

CREATE TABLE contact_job (
    id BIGINT NOT NULL AUTO_INCREMENT,
    elderly_id BIGINT NOT NULL,
    intervention_plan_id BIGINT NOT NULL,
    status VARCHAR(40) NOT NULL,
    attempt_count INT NOT NULL,
    scheduled_at DATETIME(6) NOT NULL,
    idempotency_key VARCHAR(160) NOT NULL,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uk_contact_idempotency_key (idempotency_key),
    INDEX idx_contact_status_scheduled (status, scheduled_at)
);

CREATE TABLE call_observation (
    id BIGINT NOT NULL AUTO_INCREMENT,
    contact_job_id BIGINT NOT NULL,
    contact_status VARCHAR(40) NOT NULL,
    shelter_intent VARCHAR(20) NOT NULL,
    can_move_alone VARCHAR(20) NOT NULL,
    help_needed VARCHAR(20) NOT NULL,
    symptom_mentioned VARCHAR(20) NOT NULL,
    summary VARCHAR(1000) NOT NULL,
    confidence DECIMAL(5, 4) NOT NULL,
    ended_at DATETIME(6) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uk_observation_contact_job (contact_job_id)
);

CREATE TABLE support_task (
    id BIGINT NOT NULL AUTO_INCREMENT,
    elderly_id BIGINT NOT NULL,
    contact_job_id BIGINT NULL,
    task_type VARCHAR(60) NOT NULL,
    priority VARCHAR(30) NOT NULL,
    status VARCHAR(30) NOT NULL,
    reason VARCHAR(500) NOT NULL,
    due_at DATETIME(6) NOT NULL,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    PRIMARY KEY (id),
    INDEX idx_support_status_priority_due (status, priority, due_at)
);
