import os
import pandas as pd

# Прописываем путь к обрабатываемому файлу
DATA_PATH = os.path.join("dashbrd_action.csv")


def main(path: os.path) -> None:
    """
    Top-3 winning vendors per customer for top-20 customers by number of lots

    Args:
        data (os.path): data path

    Returns:
        Excel-file: result
    """
    # Считываем данные
    data = pd.read_csv(path, delimiter=";", decimal=",", index_col=False)

    # Копируем исходный массив данных.
    actions_df = data.copy()

    # Отберем топ-20 заказчиков по частоте размещений,
    # для этого в поле actiontype_nm оставим только заказчиков и сгруппируем по полю "ur_inn_kpp"
    actions_customer_df = actions_df[actions_df["actiontype_nm"] == "заказчик"]
    top20_clients = actions_customer_df.groupby("ur_inn_kpp", as_index=False).agg(
        {"actiontype_nm": "count"}
    )

    # Отсортируем по убыванию, оставим топ-20, переименуем колонки
    top20_clients = (
        top20_clients.sort_values("actiontype_nm", ascending=False)
        .head(20)
        .reset_index(drop=True)
    )
    top20_clients.columns = ["ИНН", "Размещений"]

    # Оставляем записи, в которых заказчиком являлся кто-то из топ-20,
    # переименовываем колонку с ИНН в "ИНН Заказчика" для последующего слияния
    actions_by_top20_clients_df = actions_customer_df[
        (actions_customer_df["ur_inn_kpp"].isin(top20_clients["ИНН"]))
    ]

    actions_by_top20_clients_df = actions_by_top20_clients_df.rename(
        columns={"ur_inn_kpp": "ИНН Заказчика"}
    )[["lot_id_bas", "ИНН Заказчика"]]

    # Создадим массив записей о победителях
    actions_winner_df = actions_df[actions_df["actiontype_nm"] == "победитель"]

    # Соединяем победителей и топ-20 клиентов по лотам, группируем по паре ИНН заказчик-победитель
    actions_customers_with_winners = (
        actions_winner_df.merge(actions_by_top20_clients_df, on="lot_id_bas")
        .groupby(by=["ИНН Заказчика", "ur_inn_kpp"], as_index=False)
        .agg({"actiontype_nm": "count"})
        .sort_values(by=["ИНН Заказчика", "actiontype_nm"], ascending=False)
        .rename(
            columns={
                "ur_inn_kpp": "ИНН Победителя",
                "actiontype_nm": "Число побед Победителя",
            }
        )
    )

    # Оставляем только топ-3 вендора для каждого из 20 заказчиков
    top_clients_with_vendors = (
        actions_customers_with_winners.set_index("ИНН Победителя")
        .groupby("ИНН Заказчика")["Число побед Победителя"]
        .nlargest(3)
        .reset_index()
    )

    # Вернемся к очередности по общему количеству размещений заказчика
    top_clients_with_vendors_ordered = top20_clients.merge(
        top_clients_with_vendors, left_on="ИНН", right_on="ИНН Заказчика"
    )[top_clients_with_vendors.columns]

    # Сохраняем результат в файл excel
    top_clients_with_vendors_ordered.to_excel("task_1_result.xlsx", index=False)

    return None


if __name__ == "__main__":
    main(DATA_PATH)
