CREATE TABLE IF NOT EXISTS wanted_criminals (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100),
    nickname        VARCHAR(100) NOT NULL,
    reward          INTEGER NOT NULL,
    latitude        DOUBLE PRECISION,
    longitude       DOUBLE PRECISION,
    last_known_note TEXT,
    difficulty      INTEGER NOT NULL,
    armed           BOOLEAN NOT NULL DEFAULT FALSE,
    has_crew        BOOLEAN NOT NULL DEFAULT FALSE,
    escape_master   BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT ck_reward_non_negative CHECK (reward >= 0),
    CONSTRAINT ck_difficulty_range CHECK (difficulty BETWEEN 1 AND 10)
);
CREATE INDEX IF NOT EXISTS ix_wanted_criminals_reward ON wanted_criminals (reward);

CREATE TABLE IF NOT EXISTS hunt_logs (
    id          SERIAL PRIMARY KEY,
    criminal_id INTEGER NOT NULL REFERENCES wanted_criminals (id) ON DELETE CASCADE,
    success     BOOLEAN NOT NULL DEFAULT FALSE,
    notes       TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_hunt_logs_criminal_id ON hunt_logs (criminal_id);

/* P.S. This script was generated with the help of AI-Claudeman
   Hope you won't be too strict with me!
   Even the best hunters need ai to track unpredictable search queries ;)
*/

INSERT INTO wanted_criminals
    (name, nickname, reward, latitude, longitude, last_known_note, difficulty, armed, has_crew, escape_master)
VALUES
    ('Arman Bekov',    'Qara Barys',     250000, 43.2389,  76.9450, NULL,                                      9, TRUE,  TRUE,  TRUE),
    (NULL,             'Qyzyl Dauyl',    120000, NULL,     NULL,    'Last seen near Baikonur Cosmodrome',       7, TRUE,  TRUE,  FALSE),
    ('Aruzhan Sadyk',  'Altyn Tumar',     45000, 51.1694,  71.4491, NULL,                                      6, FALSE, FALSE, TRUE),
    ('Dias Nurgali',   'Temir Qol',        8000, 42.3155,  69.5869, NULL,                                      3, TRUE,  FALSE, FALSE),
    (NULL,             'Kok Bori',        175000, NULL,     NULL,    'Rumored to hide somewhere in the Altai mountains', 10, TRUE, TRUE, TRUE),
    ('Nurlan Askar',   'Jeti Qazyna',      3500, 49.8047,  73.1094, NULL,                                      2, FALSE, FALSE, FALSE),
    ('Zarina Kairat',  'Dala Elbasy',     22000, 43.6532,  51.1605, NULL,                                      5, TRUE,  FALSE, TRUE);


INSERT INTO hunt_logs (criminal_id, success, notes, created_at) VALUES
    (1, FALSE, 'Target escaped through the mountains near Almaty.',       NOW() - INTERVAL '30 days'),
    (1, FALSE, 'Ambushed by his crew near Kapchagay; vehicle damaged.',   NOW() - INTERVAL '21 days'),
    (2, FALSE, 'Lost the trail after leaving Baikonur.',                  NOW() - INTERVAL '18 days'),
    (2, TRUE,  'Captured near Baikonur without a fight.',                 NOW() - INTERVAL '10 days'),
    (3, FALSE, 'Disappeared from Astana railway station.',                NOW() - INTERVAL '25 days'),
    (3, FALSE, 'Used a decoy car; chased the wrong vehicle for hours.',   NOW() - INTERVAL '14 days'),
    (3, TRUE,  'Finally cornered her in a warehouse in Shymkent.',        NOW() - INTERVAL '5 days'),
    (4, TRUE,  'Surrendered after a warning shot in Turkistan.',          NOW() - INTERVAL '12 days'),
    (5, FALSE, 'No contact. Only radio silence from the Altai region.',   NOW() - INTERVAL '40 days'),
    (6, TRUE,  'Easy catch. Found him asleep in a roadside cafe.',        NOW() - INTERVAL '8 days'),
    (7, FALSE, 'Escaped using a stolen vehicle near Aktau.',              NOW() - INTERVAL '6 days'),
    (7, FALSE, 'Tracked to an oil settlement, but he slipped away again.', NOW() - INTERVAL '2 days');