from student.handlers.shop import ShopStates, show_shop_menu, show_exchange_options, process_exchange, show_bonus_catalog, show_my_bonuses

# Словарь переходов между состояниями
STATE_TRANSITIONS = {
    ShopStates.exchange: ShopStates.main,
    ShopStates.catalog: ShopStates.main,
    ShopStates.my_bonuses: ShopStates.main,
    ShopStates.main: None  # None означает возврат в главное меню
}

# Словарь обработчиков для каждого состояния
STATE_HANDLERS = {
    ShopStates.main: show_shop_menu,
    ShopStates.exchange: show_exchange_options,
    ShopStates.catalog: show_bonus_catalog,
    ShopStates.my_bonuses: show_my_bonuses
}