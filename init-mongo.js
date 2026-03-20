// MongoDB initialization script
// Creates application user for the hermod database
db = db.getSiblingDB("hermod");

db.createUser({
  user: "user",
  pwd: "change_this_password_in_production",
  roles: [{ role: "readWrite", db: "hermod" }],
});

print("Application user created for hermod database");

