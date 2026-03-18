cat > init-mongo.js << EOF
db.getSiblingDB('hermod').createUser({
  user: "user",
  pwd: "password",
  roles: [{ role: "readWrite", db: "hermod" }]
});
print("✅ Usuario creado OK");
EOF
