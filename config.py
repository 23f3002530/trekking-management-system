class Config:
    SECRET_KEY = "trekking-management-secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///trekking.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False