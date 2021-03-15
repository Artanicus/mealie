from db.database import db
from db.db_setup import generate_session
from fastapi import APIRouter, Depends
from routes.deps import manager
from schema.meal import MealPlanIn, MealPlanInDB
from schema.snackbar import SnackResponse
from schema.user import GroupInDB, UserInDB
from services.meal_services import get_todays_meal, process_meals
from sqlalchemy.orm.session import Session

router = APIRouter(prefix="/api/meal-plans", tags=["Meal Plan"])


@router.get("/all", response_model=list[MealPlanInDB])
def get_all_meals(
    current_user: UserInDB = Depends(manager),
    session: Session = Depends(generate_session),
):
    """ Returns a list of all available Meal Plan """
    print(current_user.group)
    group_entry: GroupInDB = db.groups.get(session, current_user.group, "name")
    return group_entry.mealplans


@router.post("/create")
def create_meal_plan(
    data: MealPlanIn,
    session: Session = Depends(generate_session),
    current_user=Depends(manager),
):
    """ Creates a meal plan database entry """
    processed_plan = process_meals(session, data)
    db.meals.create(session, processed_plan.dict())

    return SnackResponse.success("Mealplan Created")


@router.put("/{plan_id}")
def update_meal_plan(
    plan_id: str, meal_plan: MealPlanIn, session: Session = Depends(generate_session)
):
    """ Updates a meal plan based off ID """
    processed_plan = process_meals(session, meal_plan)
    processed_plan = MealPlanInDB(uid=plan_id, **processed_plan.dict())
    db.meals.update(session, plan_id, processed_plan.dict())

    return SnackResponse.info("Mealplan Updated")


@router.delete("/{plan_id}")
def delete_meal_plan(plan_id, session: Session = Depends(generate_session)):
    """ Removes a meal plan from the database """

    db.meals.delete(session, plan_id)

    return SnackResponse.error("Mealplan Deleted")


@router.get("/this-week", response_model=MealPlanInDB)
def get_this_week(session: Session = Depends(generate_session)):
    """ Returns the meal plan data for this week """

    return db.meals.get_all(session, limit=1, order_by="startDate")


@router.get("/today", tags=["Meal Plan"])
def get_today(session: Session = Depends(generate_session)):
    """
    Returns the recipe slug for the meal scheduled for today.
    If no meal is scheduled nothing is returned
    """

    return get_todays_meal(session)