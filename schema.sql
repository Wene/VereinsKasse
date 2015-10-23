CREATE TABLE `member_flags` (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`member_id`	INTEGER NOT NULL,
	`flag_id`	INTEGER NOT NULL
);
CREATE TABLE "members" (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`first_name`	TEXT,
	`last_name`	TEXT,
	`nick_name`	TEXT
);
CREATE TABLE "accounts" (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`name`	TEXT NOT NULL,
	`description`	TEXT,
	`bank`	TEXT,
	`number`	TEXT,
	`currency_id`	INTEGER,
	`lower_limit`	INTEGER,
	`upper_limit`	INTEGER
);
CREATE TABLE "currencies" (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`name`	TEXT NOT NULL,
	`symbol`	TEXT NOT NULL,
	`factor`	REAL NOT NULL
);
CREATE TABLE "flags" (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`name`	TEXT NOT NULL,
	`description`	TEXT,
	`value`	INTEGER,
	`interval`	TEXT
);
CREATE TABLE "transactions" (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`account_id`	INTEGER NOT NULL,
	`date`	TEXT,
	`original_text`	TEXT,
	`custom_text`	TEXT,
	`amount`	INTEGER
);
CREATE TABLE `transaction_mapping` (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`transaction_id`	INTEGER NOT NULL,
	`member_id`	INTEGER NOT NULL,
	`flag_id`	INTEGER NOT NULL
);
/* No STAT tables available */
