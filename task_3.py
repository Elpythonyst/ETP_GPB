import os
import pandas as pd
import re

# Прописываем путь к обрабатываемому файлу
DATA_PATH = os.path.join("Задание_аналитик.xlsx")


def main(path: os.path) -> None:
    """
    Extract number of procedure from comments

    Args:
        data (os.path): data path

    Returns:
        Excel-file: result
    """
    data = pd.read_excel(path)

    numbers_df = data.copy()

    # Найдём все числа в каждой записи, выберем наибольшее из них (так как часто встречается однозначный номер лота)
    numbers_df["Номер процедуры"] = (
        data["Содержание"]
        .apply(lambda x: sorted([int(y) for y in re.findall(r"\d+", x)], reverse=True))
        .str[0]
    )

    # Часто фигурирует однозначный номер лота или тарифа в отсутствие номера процедуры. Заменяем номера лотов, тарифов  и записи без чисел на "Отсутствует"
    numbers_df.iloc[
        numbers_df[numbers_df["Номер процедуры"] <= 1000].index.tolist(),
        numbers_df.columns.get_loc("Номер процедуры"),
    ] = "Отсутствует"

    numbers_df["Номер процедуры"] = numbers_df["Номер процедуры"].fillna("Отсутствует")

    # Сохраняем результат в файл excel
    numbers_df.to_excel("task_3_result.xlsx", index=False)

    return None


if __name__ == "__main__":
    main(DATA_PATH)
