"""Monster visual registry for the asset-backed renderer."""

MONSTER_LOOKS = {
    monster_id: {"asset": f"mon_{monster_id}"}
    for monster_id in (
        "rat", "bat", "goblin", "skeleton", "orc", "ogre", "troll",
        "dragon",
    )
}
