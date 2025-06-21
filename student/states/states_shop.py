from student.handlers.shop import ShopStates, show_shop_menu, show_exchange_options, process_exchange, show_bonus_catalog, show_my_bonuses, use_bonus_test

# Словарь переходов между состояниями
STATE_TRANSITIONS = {
    ShopStates.exchange: ShopStates.main,
    ShopStates.catalog: ShopStates.main,
    ShopStates.my_bonuses: ShopStates.main,
    ShopStates.purchase_confirmation: ShopStates.catalog,  # Для бонусных тестов
    ShopStates.item_purchase_confirmation: ShopStates.catalog,  # Для обычных товаров
    ShopStates.bonus_test_confirmation: ShopStates.my_bonuses,
    ShopStates.bonus_test_in_progress: ShopStates.bonus_test_confirmation,
    ShopStates.main: None  # None означает возврат в главное меню
}

# Словарь обработчиков для каждого состояния
STATE_HANDLERS = {
    ShopStates.main: show_shop_menu,
    ShopStates.exchange: show_exchange_options,
    ShopStates.catalog: show_bonus_catalog,
    ShopStates.my_bonuses: show_my_bonuses,
    ShopStates.bonus_test_confirmation: use_bonus_test,
}