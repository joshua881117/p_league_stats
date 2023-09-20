CREATE TABLE `p_league`.`year_stats`(
    `name` VARCHAR(10) NOT NULL, 
    `number` VARCHAR(10) NOT NULL, 
    `team` VARCHAR(10) NOT NULL,
    `games` INT NOT NULL, 
    `two_points_field_goals_made` INT NOT NULL, 
    `two_points_field_goals_attempt` INT NOT NULL,
    `three_points_field_goals_made` INT NOT NULL, 
    `three_points_field_goals_attempt` INT NOT NULL, 
    `free_throws_made` INT NOT NULL, 
    `free_throws_attempt` INT NOT NULL, 
    `points` INT NOT NULL,
    `offense_rebounds` INT NOT NULL, 
    `defense_rebounds` INT NOT NULL, 
    `assists` INT NOT NULL,
    `steals` INT NOT NULL, 
    `blocks` INT NOT NULL, 
    `turnovers` INT NOT NULL, 
    `personal_fouls` INT NOT NULL, 
    `playing_seconds` INT NOT NULL,
    `season` VARCHAR(10) NOT NULL,
    PRIMARY KEY(`name`, `season`)
);

CREATE TABLE `p_league`.`game_stats`(
    `player_id` INT NOT NULL,
    `game_id` INT NOT NULL,
    `points` INT NOT NULL,
    `oncourt_plus_minus` INT NOT NULL,
    `seconds` INT NOT NULL,
    `starter` INT NOT NULL,
    `turnover` INT NOT NULL,
    `ast` INT NOT NULL,
    `blk` INT NOT NULL,
    `reb_d` INT NOT NULL,
    `reb_o` INT NOT NULL,
    `pfoul` INT NOT NULL,
    `stl` INT NOT NULL,
    `trey_m` INT NOT NULL,
    `trey_a` INT NOT NULL,
    `two_m` INT NOT NULL,
    `two_a` INT NOT NULL,
    `ft_m` INT NOT NULL,
    `ft_a` INT NOT NULL,
    `team_id` INT NOT NULL,
    `number` VARCHAR(5) NOT NULL,
    PRIMARY KEY(`game_id`, `player_id`)
);

CREATE TABLE `p_league`.`player_list`(
    `id` INT NOT NULL,
    `name` VARCHAR(10) NOT NULL,
    PRIMARY KEY(`id`)
);

INSERT INTO player_list(id, name)
SELECT DISTINCT player_id, name
from game_stats;

CREATE TABLE `p_league`.`game_list`(
    `id` INT NOT NULL AUTO_INCREMENT,
    `season` VARCHAR(10) NOT NULL,
    `game` INT NOT NULL,
    `home_team_id` INT NOT NULL,
    `away_team_id` INT NOT NULL,
    PRIMARY KEY(`id`),
    UNIQUE(`season`, `game`)
);

CREATE TABLE `p_league`.`team_list`(
    `id` INT NOT NULL AUTO_INCREMENT,
    `team` VARCHAR(10) NOT NULL,
    PRIMARY KEY(`id`)
);
INSERT INTO team_list (team) VALUES
    ('臺北富邦勇士'),('高雄鋼鐵人'),('福爾摩沙台新夢想家'),
    ('桃園領航猿'),('新竹街口攻城獅'),('新北國王');