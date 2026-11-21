from extensions import db


class SystemSetting(db.Model):
    __tablename__ = 'system_settings'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.String(80), unique=True, nullable=False, index=True)
    value = db.Column(db.Text, nullable=True)
    description = db.Column(db.String(255), nullable=True)

    @classmethod
    def get_value(cls, key, default=None):
        setting = cls.query.filter_by(key=key).first()
        return setting.value if setting else default

    @classmethod
    def set_value(cls, key, value, description=None):
        setting = cls.query.filter_by(key=key).first()

        if setting:
            setting.value = str(value)
            if description:
                setting.description = description
        else:
            setting = cls(
                key=str(key),
                value=str(value),
                description=description
            )
            db.session.add(setting)

        db.session.commit()
        return setting

    def __repr__(self):
        return f'<SystemSetting {self.key}={self.value}>'
