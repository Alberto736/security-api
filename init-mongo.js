// Mongo init script executed by the official mongo image on first startup.
// It creates an application user scoped to the `hermod` database.
//
// Note: this file is executed by the legacy `mongo` shell (no process.env).
db = db.getSiblingDB("hermod");

db.createUser({
  user: "user",
  pwd: "password",
  roles: [{ role: "readWrite", db: "hermod" }],
});

print("App user created for hermod database");

