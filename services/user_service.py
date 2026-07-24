from models.user_auth import UserAuth
from schema.user_auth import UserCreate, UserSync
from utils.helper import generate_unique_id




class UserService:

    def __init__(self, db):
        self.db = db

    def create_user(self, request: UserCreate):

        user = UserAuth(
            username=request.username,
            password=request.password,
            surveyor_name=request.surveyor_name,
            email=request.email,
            mobile=request.mobile,
            zone=request.zone,
            ward=request.ward,
            surveyor_id=generate_unique_id(
                db=self.db,
                model=UserAuth,
                field_name="user_id",
                size=8,
                prefix="SUR"
            ),
            user_id=generate_unique_id(
                db=self.db,
                model=UserAuth,
                field_name="user_id",
                size=8,
                prefix="USR"
            ),
            status="Active"
        )

        self.db.add(user)
        self.db.flush()

        # user.surveyor_id = generate_surveyor_id(user.id)
        

        self.db.commit()
        self.db.refresh(user)

        return user
    
    def sync_sqlite_user(self, request: UserSync):

        user = (
            self.db.query(UserAuth)
            .filter(UserAuth.username == request.username)
            .first()
        )

        if not user:
            user = UserAuth(
                username=request.username,
                password=request.password or "",
                surveyor_name=request.surveyor_name or "",
                email=request.email,
                mobile=request.mobile,
                zone=request.zone,
                ward=request.ward,
                surveyor_id=request.surveyor_id or request.username,
                user_id=generate_unique_id(
                    db=self.db,
                    model=UserAuth,
                    field_name="user_id",
                    size=8,
                    prefix="USR"
                ),
                status="Active"
            )

            self.db.add(user)

        else:
            user.status = "Active"

        self._apply_sync_fields(user, request)

        self.db.commit()
        self.db.refresh(user)

        return self._serialize_user(user)

    def _apply_sync_fields(self, user: UserAuth, request: UserSync):
        update_fields = (
            "password",
            "ward",
            "zone",
            "surveyor_name",
            "surveyor_id",
            "mobile",
            "email",
            "access_token",
            "token_type",
            "refresh_token",
            "token_expiry",
            "last_login",
        )

        for field in update_fields:
            value = getattr(request, field)
            if value is not None:
                setattr(user, field, value)

        if request.is_logged_in is not None:
            user.is_logged_in = bool(request.is_logged_in)

    def _serialize_user(self, user: UserAuth):
        return {
            "id": user.id,
            "username": user.username,
            "ward": user.ward,
            "zone": user.zone,
            "surveyor_name": user.surveyor_name,
            "surveyor_id": user.surveyor_id,
            "mobile": user.mobile,
            "email": user.email,
            "access_token": user.access_token,
            "token_type": user.token_type,
            "refresh_token": user.refresh_token,
            "token_expiry": user.token_expiry,
            "is_logged_in": user.is_logged_in,
            "last_login": user.last_login,
        }
