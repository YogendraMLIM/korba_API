from models.survey_information import SurveyInformation
from models.user_auth import UserAuth
from schema.user_auth import UserCreate
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
            
            surveyor_id = generate_unique_id(
            db=self.db,
            model=UserAuth,
            field_name="surveyor_id",
            size=8,
            prefix="SUR"
        ),
            status="Active"
        )

        self.db.add(user)
        self.db.flush()

        # user.surveyor_id = generate_surveyor_id(user.id)
        

        self.db.commit()
        self.db.refresh(user)

        return user
    
