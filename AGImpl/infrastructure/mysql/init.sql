CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    ssn_last4 VARCHAR(4) NOT NULL,
    loyalty_tier VARCHAR(50),
    service_history TEXT
);

CREATE TABLE IF NOT EXISTS applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    income DECIMAL(15, 2),
    apr DECIMAL(5, 4),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

INSERT INTO users (name, ssn_last4, loyalty_tier, service_history)
VALUES ('John Doe', '1234', 'Platinum', '6 visits');
