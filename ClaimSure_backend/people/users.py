from fastapi import FastAPI,APIRouter,HTTPException,Depends
from ..schemas import UserCreate,ShowUser,BaseAsset,ShowAsset,CreateAsset,UpdateAsset,CreateProfile
from ..cs_db import sessionDep,User,Asset,Profile
from sqlalchemy.orm import selectinload # Import selectinload for eager loading


sessionDep = sessionDep
from sqlmodel import select,Session
from ..security import hash_pwd,get_user
from typing import Annotated




router = APIRouter()


@router.post("/create-user",response_model = ShowUser)
def create_user(user:UserCreate,session:sessionDep):
   
    usercheck = session.exec(select(User).where(User.username == user.username)).first()
    if usercheck :
        raise HTTPException(status_code=401,detail="username already exists")
   
    user_after_hash = user.model_copy(update={"pwd":hash_pwd(user.pwd)})


    db_user = User(**user_after_hash.model_dump())
    session.add(db_user)
    session.commit()
    session.refresh(db_user)


    return db_user


@router.get("/get-user",response_model=ShowUser)
def get_user(user : Annotated[ShowUser,Depends(get_user)]):
    return user


@router.post('/create-asset',response_model=ShowAsset)
def create_asset(user: Annotated[User,Depends(get_user)],session:sessionDep,asset:CreateAsset):
    nominee_id = session.exec(select(User.id).where(User.username == asset.nominee_name)).first()
    asset = Asset(**asset.model_dump(),nominee_id=nominee_id,user_id=user.id)


    session.add(asset)
    session.commit()
    session.refresh(asset)


    return asset






@router.get("/my-assets", response_model=list[ShowAsset])
def my_assets(user: Annotated[User,Depends(get_user)], session: sessionDep):
   
    assets_with_nominee = session.exec(
        select(Asset)
        .where(Asset.user_id == user.id)
        .options(selectinload(Asset.nominee))
    ).all()


    # MANUAL MAPPING: Transforms the ORM objects into the flattened response model.
    response_assets = []
    for asset in assets_with_nominee:
        # Check if nominee exists (Asset.nominee_id is not None) and retrieve the name
        nominee_name = asset.nominee.username if asset.nominee else None
       
        # Construct the flattened ShowAsset object
        response_assets.append(ShowAsset(
    **asset.model_dump(exclude={'nominee', 'user'})
))




    return response_assets


@router.get("/hello")
def hello():
    return {"msg":"hello"}




@router.put("/update-asset/{asset_id}", response_model=ShowAsset)
def update_asset(
    asset_id: int,
    new_asset: UpdateAsset,   # <-- Pydantic model with optional fields
    user: Annotated[User, Depends(get_user)],
    session: sessionDep
):
    # 1. Find the asset owned by the user
    existing_asset = session.exec(
        select(Asset)
        .where(Asset.asset_id == asset_id, Asset.user_id == user.id)
    ).first()


    if not existing_asset:
        raise HTTPException(status_code=404, detail="Asset not found or not owned by user")


    # 2. Extract update data (ignore unset + asset_id)
    update_data = new_asset.model_dump(exclude_unset=True, exclude={"asset_id"})
    if not update_data:
        raise HTTPException(status_code=400, detail="No update fields provided")


    # 3. Apply updates
    for key, value in update_data.items():
        setattr(existing_asset, key, value)


    # 4. Commit changes
    session.add(existing_asset)
    session.commit()
    session.refresh(existing_asset, attribute_names=["nominee"])  # refresh relationship


    # 5. Prepare response
    asset_data = existing_asset.model_dump(exclude={"nominee", "user"})
    asset_data["nominee_name"] = getattr(existing_asset.nominee, "username", None)  # adjust field
    return ShowAsset(**asset_data)

@router.post("/profile", response_model=CreateProfile)
def create_or_update_profile(
    profile_data: CreateProfile,
    user: Annotated[User, Depends(get_user)],
    session: sessionDep
):
    # Check if the user already has a profile
    existing_profile = session.exec(select(Profile).where(Profile.user_id == user.id)).first()

    if  existing_profile:
        raise HTTPException(status_code=404)
    
    new_profile_data = profile_data.model_dump()
    new_profile = Profile(user_id=user.id, **new_profile_data)
    session.add(new_profile)
    session.commit()
    session.refresh(new_profile)
    return new_profile




@router.get("/get-profile",response_model=Profile)
def get_profile(user:Annotated[User,Depends(get_user)],session:sessionDep):

    profile = session.exec(select(Profile).where(Profile.user_id == user.id)).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return profile


@router.get("/recieved-assets")
def recieved_assets(user:Annotated[User,Depends(get_user)],session:sessionDep):
    assets_with_nominee = session.exec(
        select(Asset)
        .where(Asset.nominee_id == user.id)
        .options(selectinload(Asset.nominee))
    ).all()


    # MANUAL MAPPING: Transforms the ORM objects into the flattened response model.
    response_assets = []
    for asset in assets_with_nominee:
        # Check if nominee exists (Asset.nominee_id is not None) and retrieve the name
        nominee_name = asset.nominee.username if asset.nominee else None
       
        # Construct the flattened ShowAsset object
        response_assets.append(ShowAsset(
    **asset.model_dump(exclude={'nominee', 'user'})
))

    return response_assets

    