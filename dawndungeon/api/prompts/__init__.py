
from langchain import PromptTemplate
from textwrap import dedent

CHARACTER_METADATA_TEMPLATE: str = dedent("""
    The metadata should be a dictionary that contains information about the character in your story.

    [Character] Attributes
    - name: str
    - description: str
    - age: Optional[int]
    - coins: Optional[int]
    - current_health: Optional[int]
    - current_mana: Optional[int]
    - defense: Optional[int]
    - health_regeneration: Optional[int]
    - inventory: Optional[List[Item]]
    - level: Optional[int]
    - location: Optional[str]
    - mana_regeneration: Optional[int]
    - max_health: Optional[int]
    - max_mana: Optional[int]
    - quests: Optional[List[Quest]]
    - strength: Optional[int]

    [Item] Attributes
    - name: str
    - description: str
    - damage: Optional[int]
    - durability: Optional[int]
    - price: Optional[float]

    [Quest] Attributes
    - title: str
    - description: str
    - rewards: Optional[Reward]

    [Reward] Attributes
    - coins: Optional[int]
    - items: Optional[List[Item]]

    """
)

WORLD_METADATA_TEMPLATE: str = dedent("""
    The metadata should be a dictionary that contains information about the world in your story.

    [World] Attributes
    - name: str
    - description: str
    - artifacts: Optional[List[str]]
    - current_date: Optional[str]
    - current_time: Optional[str]
    - dimensions: Optional[List[str]]
    - geography: Optional[str]
    - history: Optional[str]
    - magic: Optional[str]
    - technology: Optional[str]
    - threat_level: Optional[str]
    - world_quests: Optional[List[str]]

    """
)

METADATA_EXAMPLE_TEMPLATE: str = dedent("""
    Your task is to create a response in JSON format. This JSON should have two parts:
    1. "content": This is a string that should contain a story. For example, "You are in a forest."
    2. "metadata": This is a dictionary that contains information about a character in your story.

    Here's an example of what your JSON response should look like:

    {{
        "content": "This is where you write your own story. For example, 'You are in a forest.'",
        "metadata": {{
            "character": {{
                "name": "This is where you put the name of a character in your story. For example, 'John'",
                "description": "A brief description of the character. For example, 'A normal guy'",
                "age": "The age of the character. For example, 20",
                "coins": "The number of coins the character has. For example, 0",
                "current_health": "The current health of the character. For example, 100",
                "current_mana": "The current mana of the character. For example, 100",
                "defense": "The defense of the character. For example, 1",
                "dimension": "The current dimension of the character. For example, 'Earth'",
                "health_regeneration": "The health regeneration of the character. For example, 1",
                "inventory": "The items that the character has. Each item has a name, description, damage, durability, and price."
                "level": "The level of the character. For example, 1",
                "location": "The current location of the character. For example, 'Forest'",
                "max_health": "The maximum health of the character. For example, 100",
                "max_mana": "The maximum mana of the character. For example, 100",
                "quests": "The quests that the character has. Each quest has a title, description, and rewards. Rewards can be coins or items.",
                "strength": "The strength of the character. For example, 1",
            }},
            "world": {{
                "name": "This is where you put the name of the world. For example, 'Fantasy Land'",
                "description": "A brief description of the world. For example, 'A land filled with magic and wonder'",
                "world_quest": "The current critic quest in the world, if any. Each quest has a title, description, and rewards. Rewards can be coins or items.",
                "artifacts": "The artifacts that exist in the world. Each artifact is a string. For example, ['Excalibur', 'Holy Grail']",
                "current_date": "The current date in the world, if applicable. For example, 'June 23, 2023'",
                "current_time": "The current time in the world, if applicable. For example, '12:00 PM'",
                "dimensions": "The different dimensions in the world, if any. Each dimension is a string. For example, ['Earth', 'Underworld']",
                "geography": "A brief description of the world's geography. For example, 'Mountains, forests, and rivers'",
                "history": "A brief description of the world's history. For example, 'A history of wars and peace'",
                "magic": "A brief description of the role of magic in the world. For example, 'Magic is common and is used daily'",
                "technology": "A brief description of the level of technology in the world. For example, 'Medieval technology'",
                "threat_level": "The current threat level in the world. For example, 'Low'"
            }}
        }}
    }}
    """
)


INIT_WORLD_TEMPLATE: PromptTemplate = PromptTemplate(
    input_variables=["world_name", "world_description"],
    template=dedent("""
    You are the master of a story set in a world named {world_name},
    which is described as {world_description}.

    Your task is to create a unique character for the player.
    This character can have a starting quest or some items in their inventory to begin with.

    However, you must ensure that the character you create is different from any examples provided.
    Also, you should not ask the player to input any attributes for the character themselves.
    You need to generate all the character's attributes on your own.

    """ + \
        CHARACTER_METADATA_TEMPLATE + \
        WORLD_METADATA_TEMPLATE + \
        METADATA_EXAMPLE_TEMPLATE
    )
)


EXECUTE_WORLD_TEMPLATE: PromptTemplate = PromptTemplate(
    input_variables=["storylines", "metadata", "action"],
    template=dedent("""
    As the master of the story, your task is to continue the story based on the given storylines and the next action of the character.

    """ + \
        CHARACTER_METADATA_TEMPLATE + \
        WORLD_METADATA_TEMPLATE + \
        dedent("""

        Here are the datas from the previous turn:

        Storylines: [
            {storylines}
        ]

        The next action of the character is: "{action}"

        The metadata of the previous storyline is provided in JSON format:
        ```json
        {metadata}
        ```

        Your task is to create a response in JSON format, which contains two keys:
        1. "content": This is a string that should contain a story. For example, "You are in a forest."
        2. "metadata": This is a dictionary that contains information about a character in your story.

        You should call the character as "you" and the world as "the world".
        You should not generate the same storyline as the last turn.
        In the "metadata" dictionary, you should copy the metadata from the previous turn, and adjust it based on the action and the new storyline with the following rules:

        Your new storyline should be based on this metadata.
        Here are some examples of how you can do this:
            - If the character doesn't have an item needed to complete an action, you could create a storyline where the character can't complete the action, or where they find the item.
            - If the character doesn't have enough coins, you could create a storyline where the character can't buy an item.
            - If the character doesn't have mana, you could create a storyline where the character can't use magic.
            - If the character has a high level, you could create a storyline where the character is asked to accept a dangerous quest.
            - If the character has health regeneration, you could slightly increase their health based on this stat.
            - If the character is dead, you could create a storyline where the character can't complete the action, or where they are revived.
            - If the threat in the world has been eliminated, you could change the world's metadata to reflect this.
            - If the world has a high threat level, you could create a storyline where the character has to fight a monster.
            - If the world has world quests, you could create a storyline where the character is asked to accept or reject the quest.

        Please note that you can't change fixed attributes of the character, such as their name or description.
        However, you can change other attributes, such as their coins, current health, or inventory, based on the action.
        For example,
            - If the action leads to a fight, you could change the character's current health, and increase their level if they win.
            - If the action leads to a new dimension, you could change the character's dimension.
            - If the action leads to a new item, you could change the character's inventory.
            - If the action leads to a new location, you could change the character's location.
            - If the action leads to a new quest, you could add the quest to the character's quests.
            - If the action leads to a new threat level, you could change the world's threat level.
            - If the action leads to a reward, you could change the character's coins or inventory.
            - If the action leads to buying an item, you could change the character's coins and inventory.
            - If the action leads to completion of a quest, you could remove the quest from the character's quests.
            - If the character finds a chest, you could add the items in the chest to the character's inventory or coins.
            - If the storyline is about the character's death, you could change the character's health to 0.
            - If the time passes, you could change the world's current date and time.
            - You may randomly generate new world quests, artifacts, or dimensions in the world, if needed.
            - You may randomly generate some of the attributes, such as the character's health or mana, if needed.


        Remember, your response should only contain this JSON format and nothing else.
        """)
    )
)
