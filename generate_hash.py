from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
password = "Souilhi8"  # ton nouveau mot de passe
hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")
print(hashed_pw)