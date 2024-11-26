import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# Создание точного датасета
def generate_precise_data(n_samples_per_age=10):
    # Точные исходные данные
    data = {
        'Age': [18, 19, 20, 21, 22, 23, 24, 25, 26, 27],
        'Awareness_Level': [2, 3, 4, 5, 4, 3, 5, 6, 7, 8],
        'Usage_Level': [3, 4, 5, 6, 5, 4, 6, 7, 8, 9]
    }
    
    # Расширение данных
    expanded_data = []
    for age, awareness, usage in zip(data['Age'], data['Awareness_Level'], data['Usage_Level']):
        for _ in range(n_samples_per_age):
            expanded_data.append({
                'Age': age,
                'Awareness_Level': max(0, min(10, awareness + np.random.normal(0, 1))),
                'Usage_Level': max(0, min(10, usage + np.random.normal(0, 1)))
            })
    
    return pd.DataFrame(expanded_data)

# Генерация данных
df = generate_precise_data()

# Подготовка данных для длинного формата
df_long = pd.melt(df, id_vars=['Age'], value_vars=['Awareness_Level', 'Usage_Level'], 
                  var_name='Metric', value_name='Level')

# Создание графика
plt.figure(figsize=(12, 6))
sns.violinplot(x='Age', y='Level', hue='Metric', data=df_long, split=True)
plt.title('Осведомленность и использование тайм-менеджмента по возрастам')
plt.xlabel('Возраст')
plt.ylabel('Уровень (1-10)')
plt.legend(title='Метрика')
plt.tight_layout()
plt.show()

# Анализ данных
print("Анализ данных об осведомленности и использовании тайм-менеджмента:")

# Группировка по возрастам и вычисление средних
age_metrics = df.groupby('Age')[['Awareness_Level', 'Usage_Level']].mean()
print("\nСредние показатели по возрастным группам:")
print(age_metrics)

print("\nОбщая статистика:")
print("Средняя осведомленность:", df['Awareness_Level'].mean())
print("Средний уровень использования:", df['Usage_Level'].mean())

print("\nКорреляция между возрастом и метриками:")
print("Корреляция возраста и осведомленности:", 
      df['Age'].corr(df['Awareness_Level']))
print("Корреляция возраста и использования:", 
      df['Age'].corr(df['Usage_Level']))