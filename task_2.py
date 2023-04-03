import os
import pandas as pd

# Прописываем путь к обрабатываемому файлу
DATA_PATH = os.path.join("dashbrd_action.csv")


def main(path: os.path) -> None:
    """
    Top-5 customers by month in last 6 months

    Args:
        data (os.path): data path

    Returns:
        Excel-file: result
    """
    # Считываем данные
    data = pd.read_csv(path, delimiter=";", decimal=",", index_col=False)

    # Копируем исходный массив данных. Преобразуем время в подходящий формат
    actions_df = data.copy()
    actions_df["timestamp"] = pd.to_datetime(
        actions_df["timestamp"].str[:-6], format="%Y-%m-%d %H:%M:%S"
    )

    # Будем рассматривать последние доступные полгода - до декабря 2020 года.
    # Оставляем только записи 7 и более месяца 2020 года с действующим лицом "заказчик"
    actions_df = actions_df[
        (actions_df["timestamp"].dt.year == 2020)
        & (actions_df["timestamp"].dt.month >= 7)
        & (actions_df["actiontype_nm"] == "заказчик")
    ]

    # Вычленяем месяц из даты
    actions_df["Месяц"] = actions_df["timestamp"].dt.month

    # Группируем по месяцу, ИНН
    actions_df_grouped = (
        actions_df.groupby(by=["Месяц", "ur_inn_kpp"], as_index=False)
        .agg({"actiontype_nm": "count"})
        .sort_values(by=["Месяц", "actiontype_nm"], ascending=False)
        .rename(columns={"ur_inn_kpp": "ИНН", "actiontype_nm": "Число размещений"})
    )

    # Оставляем только топ-5 заказчиков по числу размещений по месяцам
    actions_df_grouped = (
        actions_df_grouped.set_index("ИНН")
        .groupby("Месяц")["Число размещений"]
        .nlargest(5)
        .reset_index()
    )

    # Сохраняем результат в файл excel
    actions_df_grouped.to_excel("task_2_result.xlsx", index=False)

    return None


if __name__ == "__main__":
    main(DATA_PATH)
