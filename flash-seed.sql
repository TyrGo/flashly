-- Test users have password "password"

INSERT INTO users (username, password, is_admin)
VALUES ('testuser',
        '$2b$12$AZH7virni5jlTTiGgEg4zu3lSvAw68qVEfSIOjJ3RqtbJbdW/Oi5q',
        False),
       ('testadmin',
        '$2b$12$AZH7virni5jlTTiGgEg4zu3lSvAw68qVEfSIOjJ3RqtbJbdW/Oi5q',
        TRUE);

INSERT INTO cards (word, defn, bin, wrongs, user_id, due) 
VALUES ('Cat', 'This animal meows', 0, 0, 1, CURRENT_TIMESTAMP),
        ('Dog', 'This animal barks', 0, 0, 1, CURRENT_TIMESTAMP),
        ('Mouse', 'This animal squeeks', 0, 0, 1, CURRENT_TIMESTAMP),
        ('Bird', 'This animal chrips', 0, 0, 1, CURRENT_TIMESTAMP),
        ('Tiger', 'This animal roars', 0, 0, 1, CURRENT_TIMESTAMP),
        ('Cookie', 'Little data stored by browser', 0, 0, 2, CURRENT_TIMESTAMP),
        ('Flatten', 'Popularly recursive function for lists', 0, 0, 2, CURRENT_TIMESTAMP),
        ('APL', 'A Programming Language', 0, 0, 2, CURRENT_TIMESTAMP);