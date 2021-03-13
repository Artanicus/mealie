import datetime
from datetime import date
from typing import List

import sqlalchemy as sa
import sqlalchemy.orm as orm
from db.models.model_base import BaseMixins, SqlAlchemyBase
from db.models.recipe.api_extras import ApiExtras
from db.models.recipe.category import Category, recipes2categories
from db.models.recipe.ingredient import RecipeIngredient
from db.models.recipe.instruction import RecipeInstruction
from db.models.recipe.note import Note
from db.models.recipe.nutrition import Nutrition
from db.models.recipe.tag import Tag, recipes2tags
from db.models.recipe.tool import Tool
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import validates


class RecipeModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "recipes"
    # Database Specific
    id = sa.Column(sa.Integer, primary_key=True)

    # General Recipe Properties
    name = sa.Column(sa.String, nullable=False)
    description = sa.Column(sa.String)
    image = sa.Column(sa.String)
    totalTime = sa.Column(sa.String)
    prepTime = sa.Column(sa.String)
    performTime = sa.Column(sa.String)
    cookTime = sa.Column(sa.String)
    recipeYield = sa.Column(sa.String)
    recipeCuisine = sa.Column(sa.String)
    tool: List[Tool] = orm.relationship("Tool", cascade="all, delete")
    nutrition: Nutrition = orm.relationship(
        "Nutrition", uselist=False, cascade="all, delete"
    )
    recipeCategory: List = orm.relationship(
        "Category", secondary=recipes2categories, back_populates="recipes"
    )

    recipeIngredient: List[RecipeIngredient] = orm.relationship(
        "RecipeIngredient",
        cascade="all, delete",
        order_by="RecipeIngredient.position",
        collection_class=ordering_list("position"),
    )
    recipeInstructions: List[RecipeInstruction] = orm.relationship(
        "RecipeInstruction",
        cascade="all, delete",
        order_by="RecipeInstruction.position",
        collection_class=ordering_list("position"),
    )

    # Mealie Specific
    slug = sa.Column(sa.String, index=True, unique=True)
    tags: List[Tag] = orm.relationship(
        "Tag", secondary=recipes2tags, back_populates="recipes"
    )
    dateAdded = sa.Column(sa.Date, default=date.today)
    notes: List[Note] = orm.relationship("Note", cascade="all, delete")
    rating = sa.Column(sa.Integer)
    orgURL = sa.Column(sa.String)
    extras: List[ApiExtras] = orm.relationship("ApiExtras", cascade="all, delete")

    @validates("name")
    def validate_name(self, key, name):
        assert not name == ""
        return name

    def __init__(
        self,
        session,
        name: str = None,
        description: str = None,
        image: str = None,
        recipeYield: str = None,
        recipeIngredient: List[str] = None,
        recipeInstructions: List[dict] = None,
        recipeCuisine: str = None,
        totalTime: str = None,
        prepTime: str = None,
        nutrition: dict = None,
        tool: list[str] = [],
        performTime: str = None,
        slug: str = None,
        recipeCategory: List[str] = None,
        tags: List[str] = None,
        dateAdded: datetime.date = None,
        notes: List[dict] = None,
        rating: int = None,
        orgURL: str = None,
        extras: dict = None,
    ) -> None:
        self.name = name
        self.description = description
        self.image = image
        self.recipeCuisine = recipeCuisine

        if self.nutrition:
            self.nutrition = Nutrition(**nutrition)
        else:
            self.nutrition = Nutrition()

        self.tool = [Tool(tool=x) for x in tool] if tool else []

        self.recipeYield = recipeYield
        self.recipeIngredient = [
            RecipeIngredient(ingredient=ingr) for ingr in recipeIngredient
        ]
        self.recipeInstructions = [
            RecipeInstruction(text=instruc.get("text"), type=instruc.get("@type", None))
            for instruc in recipeInstructions
        ]
        self.totalTime = totalTime
        self.prepTime = prepTime
        self.performTime = performTime

        self.recipeCategory = [
            Category.create_if_not_exist(session=session, name=cat)
            for cat in recipeCategory
        ]

        # Mealie Specific
        self.tags = [Tag.create_if_not_exist(session=session, name=tag) for tag in tags]
        self.slug = slug
        self.dateAdded = dateAdded
        self.notes = [Note(**note) for note in notes]
        self.rating = rating
        self.orgURL = orgURL
        self.extras = [ApiExtras(key=key, value=value) for key, value in extras.items()]

    def update(
        self,
        session,
        name: str = None,
        description: str = None,
        image: str = None,
        recipeYield: str = None,
        recipeIngredient: List[str] = None,
        recipeInstructions: List[dict] = None,
        recipeCuisine: str = None,
        totalTime: str = None,
        tool: list[str] = [],
        prepTime: str = None,
        performTime: str = None,
        nutrition: dict = None,
        slug: str = None,
        recipeCategory: List[str] = None,
        tags: List[str] = None,
        dateAdded: datetime.date = None,
        notes: List[dict] = None,
        rating: int = None,
        orgURL: str = None,
        extras: dict = None,
    ):
        """Updated a database entry by removing nested rows and rebuilds the row through the __init__ functions"""
        list_of_tables = [RecipeIngredient, RecipeInstruction, ApiExtras, Tool]
        RecipeModel._sql_remove_list(session, list_of_tables, self.id)

        self.__init__(
            session=session,
            name=name,
            description=description,
            image=image,
            recipeYield=recipeYield,
            recipeIngredient=recipeIngredient,
            recipeInstructions=recipeInstructions,
            totalTime=totalTime,
            recipeCuisine=recipeCuisine,
            prepTime=prepTime,
            performTime=performTime,
            nutrition=nutrition,
            tool=tool,
            slug=slug,
            recipeCategory=recipeCategory,
            tags=tags,
            dateAdded=dateAdded,
            notes=notes,
            rating=rating,
            orgURL=orgURL,
            extras=extras,
        )
