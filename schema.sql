-- WMS Prototype Schema
-- PostgreSQL

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE products (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku             VARCHAR(100) NOT NULL UNIQUE,
    name            VARCHAR(255) NOT NULL,
    reorder_point   INT NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE channels (
    id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name    VARCHAR(100) NOT NULL UNIQUE,
    type    VARCHAR(50)  NOT NULL
);

CREATE TABLE inventory_levels (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id          UUID NOT NULL REFERENCES products(id),
    channel_id          UUID NOT NULL REFERENCES channels(id),
    quantity_on_hand    INT NOT NULL DEFAULT 0 CHECK (quantity_on_hand >= 0),
    quantity_reserved   INT NOT NULL DEFAULT 0 CHECK (quantity_reserved >= 0),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (product_id, channel_id)
);

CREATE TABLE inventory_transactions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id          UUID NOT NULL REFERENCES products(id),
    channel_id          UUID NOT NULL REFERENCES channels(id),
    type                VARCHAR(50) NOT NULL,
    quantity_delta      INT NOT NULL,
    note                TEXT,
    idempotency_key     VARCHAR(255) UNIQUE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE sku_mappings (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id  UUID NOT NULL REFERENCES products(id),
    channel_id  UUID NOT NULL REFERENCES channels(id),
    channel_sku VARCHAR(200) NOT NULL,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (channel_id, channel_sku)
);

-- 인덱스
CREATE INDEX idx_inventory_levels_product
    ON inventory_levels(product_id);
CREATE INDEX idx_inventory_transactions_product
    ON inventory_transactions(product_id);
CREATE INDEX idx_sku_mappings_channel_sku
    ON sku_mappings(channel_id, channel_sku);

-- 기본 채널 데이터
INSERT INTO channels (name, type) VALUES
    ('warehouse', 'internal'),
    ('shopify',   'marketplace'),
    ('amazon',    'marketplace'),
    ('walmart',   'marketplace');