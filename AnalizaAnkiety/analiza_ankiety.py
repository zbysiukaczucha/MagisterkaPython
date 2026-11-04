import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import os

warnings.filterwarnings("ignore")


def analizuj_ankiete(sciezka_excel):
    print("Rozpoczynam analizę wyników ankiety...")
    df = pd.read_excel(sciezka_excel)

    # =========================================================
    # DEFINICJE LOGICZNEJ KOLEJNOŚCI (DANE PORZĄDKOWE)
    # =========================================================
    kolejnosc_wiek = ['Poniżej 18 lat', '18 – 26 lat', '27 – 35 lata', '36 – 45 lat', '45 lat i więcej']
    kolejnosc_doswiadczenie = ['Brak doświadczenia', 'Gram rzadko', 'Gram od czasu do czasu', 'Gram często',
                               'Zajmuję się tworzeniem gier']

    # =========================================================
    # 1. DEMOGRAFIA (Wykresy kołowe z logicznym sortowaniem)
    # =========================================================
    fig = plt.figure(figsize=(12, 10))
    gs = fig.add_gridspec(2, 4)

    ax1 = fig.add_subplot(gs[0, 0:2])
    ax2 = fig.add_subplot(gs[0, 2:4])
    ax3 = fig.add_subplot(gs[1, 1:3])

    kolory = sns.color_palette('pastel')

    # Płeć (tutaj sortujemy normalnie po wielkości)
    plec = df.iloc[:, 1].value_counts()
    ax1.pie(plec, labels=plec.index, autopct='%1.1f%%', colors=kolory, startangle=140, textprops={'fontsize': 12})
    ax1.set_title('Płeć respondentów', fontweight='bold', fontsize=16)

    # Wiek (wymuszamy logiczną kolejność)
    wiek = df.iloc[:, 2].value_counts()
    wiek = wiek.reindex([w for w in kolejnosc_wiek if w in wiek.index])
    ax2.pie(wiek, labels=wiek.index, autopct='%1.1f%%', colors=sns.color_palette('Set2'), startangle=140,
            textprops={'fontsize': 12})
    ax2.set_title('Przedział wiekowy', fontweight='bold', fontsize=16)

    # Doświadczenie (Czyszczenie, łączenie i logiczna kolejność)
    doswiadczenie_surowe = df.iloc[:, 3].copy()
    mapowanie_doswiadczenia = {
        'Czasem gram': 'Gram od czasu do czasu',
        'Gram od czasu do czasu': 'Gram od czasu do czasu',
        'Gram rzadko': 'Gram rzadko',
        'Gram często': 'Gram często',
        'Zajmuję się tworzeniem gier': 'Zajmuję się tworzeniem gier',
        'Żadne': 'Brak doświadczenia'
    }
    doswiadczenie_czyste = doswiadczenie_surowe.replace(mapowanie_doswiadczenia).value_counts()
    doswiadczenie_czyste = doswiadczenie_czyste.reindex(
        [d for d in kolejnosc_doswiadczenie if d in doswiadczenie_czyste.index])

    ax3.pie(doswiadczenie_czyste, labels=doswiadczenie_czyste.index, autopct='%1.1f%%',
            colors=sns.color_palette('Set3'), startangle=140, textprops={'fontsize': 12})
    ax3.set_title('Doświadczenie w grach wideo', fontweight='bold', fontsize=16)

    plt.tight_layout()
    plt.savefig('Ankieta_01_Demografia.png', dpi=300)
    plt.close()
    print("Wygenerowano wykres 01: Demografia (kolejność logiczna)")

    # =========================================================
    # 2. WYBÓR NAJLEPSZEGO WARIANTU (Zsumowane 3 utwory ogółem)
    # =========================================================
    wybory = pd.concat([df.iloc[:, 13], df.iloc[:, 23], df.iloc[:, 33]])
    wybory_counts = wybory.value_counts().reset_index()
    wybory_counts.columns = ['Wariant', 'Liczba głosów']

    plt.figure(figsize=(10, 6))
    sns.barplot(x='Wariant', y='Liczba głosów', data=wybory_counts, palette='viridis')
    plt.title('Który wariant najlepiej wizualnie reprezentuje utwór muzyczny? (Suma głosów)', fontweight='bold')
    plt.ylabel('Liczba oddanych głosów', fontsize=14)
    plt.xlabel('Model terenu', fontsize=14, labelpad=10)

    for index, row in wybory_counts.iterrows():
        plt.text(index, row['Liczba głosów'] + 0.2, str(row['Liczba głosów']), color='black', ha="center",
                 fontweight='bold')

    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('Ankieta_02_NajlepszyWariant.png', dpi=300)
    plt.close()
    print("Wygenerowano wykres 02: Najlepszy wariant")

    # =========================================================
    # 3. ŚREDNIE OCENY MODELI W SKALI LIKERTA (1-5)
    # =========================================================
    mapa_ocen = {
        'Bardzo źle': 1, 'Źle': 2, 'Neutralnie': 3, 'Dobrze': 4, 'Bardzo dobrze': 5,
        1: 1, 2: 2, 3: 3, 4: 4, 5: 5
    }
    df_num = df.replace(mapa_ocen)

    estetyka_A = pd.concat([df_num.iloc[:, 4], df_num.iloc[:, 14], df_num.iloc[:, 24]]).astype(float).mean()
    estetyka_B = pd.concat([df_num.iloc[:, 7], df_num.iloc[:, 17], df_num.iloc[:, 27]]).astype(float).mean()
    estetyka_C = pd.concat([df_num.iloc[:, 10], df_num.iloc[:, 20], df_num.iloc[:, 30]]).astype(float).mean()

    geologia_A = pd.concat([df_num.iloc[:, 5], df_num.iloc[:, 15], df_num.iloc[:, 25]]).astype(float).mean()
    geologia_B = pd.concat([df_num.iloc[:, 8], df_num.iloc[:, 18], df_num.iloc[:, 28]]).astype(float).mean()
    geologia_C = pd.concat([df_num.iloc[:, 11], df_num.iloc[:, 21], df_num.iloc[:, 31]]).astype(float).mean()

    dynamika_A = pd.concat([df_num.iloc[:, 6], df_num.iloc[:, 16], df_num.iloc[:, 26]]).astype(float).mean()
    dynamika_B = pd.concat([df_num.iloc[:, 9], df_num.iloc[:, 19], df_num.iloc[:, 29]]).astype(float).mean()
    dynamika_C = pd.concat([df_num.iloc[:, 12], df_num.iloc[:, 22], df_num.iloc[:, 32]]).astype(float).mean()

    dane_oceny = pd.DataFrame({
        'Kategoria oceny': ['Ogólna estetyka', 'Ogólna estetyka', 'Ogólna estetyka',
                            'Naturalny wygląd', 'Naturalny wygląd', 'Naturalny wygląd',
                            'Oddanie dynamiki audio', 'Oddanie dynamiki audio', 'Oddanie dynamiki audio'],
        'Model': ['Model A', 'Model B', 'Model C', 'Model A', 'Model B', 'Model C', 'Model A', 'Model B', 'Model C'],
        'Średnia ocena (1-5)': [estetyka_A, estetyka_B, estetyka_C, geologia_A, geologia_B, geologia_C, dynamika_A,
                                dynamika_B, dynamika_C]
    })

    plt.figure(figsize=(14, 7))
    sns.barplot(x='Kategoria oceny', y='Średnia ocena (1-5)', hue='Model', data=dane_oceny, palette='Set2')
    plt.title('Średnie oceny modeli w kluczowych aspektach wizualnych (Skala 1-5)', fontweight='bold', fontsize=16)
    plt.ylim(1, 5)
    plt.ylabel('Średnia ocena', fontsize=16)
    plt.xlabel('Kategoria oceny', fontsize=16, labelpad=20)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.legend(title='Model', loc='upper right')

    for p in plt.gca().patches:
        plt.gca().annotate(f'{p.get_height():.2f}',
                           (p.get_x() + p.get_width() / 2., p.get_height()),
                           ha='center', va='center',
                           xytext=(0, 9), textcoords='offset points')

    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('Ankieta_03_SrednieOceny.png', dpi=300)
    plt.close()
    print("Wygenerowano wykres 03: Średnie oceny modeli")

    # =========================================================
    # 4. KORELACJA WYBORÓW Z DEMOGRAFIĄ
    # =========================================================
    demo = df.iloc[:, [1, 2, 3]].copy()
    demo.columns = ['Płeć', 'Wiek', 'Doświadczenie']
    demo['Doświadczenie'] = demo['Doświadczenie'].replace(mapowanie_doswiadczenia)

    wybory_1 = demo.copy()
    wybory_1['Wybór Modelu'] = df.iloc[:, 13]

    wybory_2 = demo.copy()
    wybory_2['Wybór Modelu'] = df.iloc[:, 23]

    wybory_3 = demo.copy()
    wybory_3['Wybór Modelu'] = df.iloc[:, 33]

    wszystkie_glosy = pd.concat([wybory_1, wybory_2, wybory_3]).dropna(subset=['Wybór Modelu']).reset_index(drop=True)

    fig, axes = plt.subplots(3, 1, figsize=(12, 18))
    kolejnosc_modeli = ['Model A', 'Model B', 'Model C']

    # Filtrowanie legendy, aby pokazywały się tylko te kategorie, które faktycznie wystąpiły w ankiecie
    obecne_wieki = [w for w in kolejnosc_wiek if w in wszystkie_glosy['Wiek'].unique()]
    obecne_doswiadczenia = [d for d in kolejnosc_doswiadczenie if d in wszystkie_glosy['Doświadczenie'].unique()]

    # 4.1 Wybór a Płeć
    cross_plec = pd.crosstab(wszystkie_glosy['Wybór Modelu'], wszystkie_glosy['Płeć'], normalize='columns') * 100
    cross_plec = cross_plec.reindex(index=kolejnosc_modeli).fillna(0)
    cross_plec.plot(kind='bar', ax=axes[0], color=sns.color_palette('Pastel1'), width=0.8)
    axes[0].set_title('Preferencje wyboru modelu z podziałem na płeć', fontweight='bold', fontsize=16)
    axes[0].set_ylabel('Procent głosów w podgrupie [%]')
    axes[0].set_xlabel('')
    axes[0].legend(title='Płeć', loc='upper left')
    axes[0].tick_params(axis='x', rotation=0)
    axes[0].set_ylim(0, 100)

    # 4.2 Wybór a Wiek
    cross_wiek = pd.crosstab(wszystkie_glosy['Wybór Modelu'], wszystkie_glosy['Wiek'], normalize='columns') * 100
    cross_wiek = cross_wiek.reindex(index=kolejnosc_modeli, columns=obecne_wieki).fillna(0)
    cross_wiek.plot(kind='bar', ax=axes[1], color=sns.color_palette('Set2'), width=0.8)
    axes[1].set_title('Preferencje wyboru modelu z podziałem na wiek', fontweight='bold', fontsize=16)
    axes[1].set_ylabel('Procent głosów w podgrupie [%]')
    axes[1].set_xlabel('')
    axes[1].legend(title='Wiek', loc='upper left')
    axes[1].tick_params(axis='x', rotation=0)
    axes[1].set_ylim(0, 100)

    # 4.3 Wybór a Doświadczenie w grach
    cross_dosw = pd.crosstab(wszystkie_glosy['Wybór Modelu'], wszystkie_glosy['Doświadczenie'],
                             normalize='columns') * 100
    cross_dosw = cross_dosw.reindex(index=kolejnosc_modeli, columns=obecne_doswiadczenia).fillna(0)
    cross_dosw.plot(kind='bar', ax=axes[2], color=sns.color_palette('Set3'), width=0.8)
    axes[2].set_title('Preferencje wyboru modelu z podziałem na doświadczenie w grach wideo', fontweight='bold',
                      fontsize=16)
    axes[2].set_ylabel('Procent głosów w podgrupie [%]')
    axes[2].set_xlabel('Model terenu')
    axes[2].legend(title='Doświadczenie', loc='upper left')
    axes[2].tick_params(axis='x', rotation=0)
    axes[2].set_ylim(0, 100)

    for ax in axes:
        ax.grid(axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.savefig('Ankieta_04_Demografia_Wybory.png', dpi=300)
    plt.close()
    print("Wygenerowano wykres 04: Preferencje wyboru modelu z podziałem demograficznym")

    # =========================================================
    # 5. KORELACJA WYBORÓW Z UTWOREM
    # =========================================================
    wybory_utwor_1 = df.iloc[:, 13]
    wybory_utwor_2 = df.iloc[:, 23]
    wybory_utwor_3 = df.iloc[:, 33]

    df_wybory_utwory = pd.DataFrame({
        'Utwór': ['Utwór 1 (Ambient)'] * len(wybory_utwor_1) +
                 ['Utwór 2 (Rock)'] * len(wybory_utwor_2) +
                 ['Utwór 3 (Trap)'] * len(wybory_utwor_3),
        'Wybór Modelu': pd.concat([wybory_utwor_1, wybory_utwor_2, wybory_utwor_3]).values
    })

    df_wybory_utwory.dropna(inplace=True)

    plt.figure(figsize=(10, 6))
    ax_utwory = sns.countplot(
        data=df_wybory_utwory,
        x='Utwór',
        hue='Wybór Modelu',
        palette='viridis',
        hue_order=kolejnosc_modeli
    )

    plt.title('Preferencje wyboru modelu terenu w zależności od utworu muzycznego', fontweight='bold', fontsize=14)
    plt.ylabel('Liczba oddanych głosów', fontsize=14)
    plt.xlabel('Zastosowana próbka dźwiękowa', fontsize=14, labelpad=10)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.legend(title='Wybór modelu', loc='upper left')

    plt.grid(axis='y', linestyle='--', alpha=0.7)

    for p in ax_utwory.patches:
        height = p.get_height()
        if height > 0:
            ax_utwory.annotate(
                f'{int(height)}',
                (p.get_x() + p.get_width() / 2., height),
                ha='center',
                va='bottom',
                fontweight='bold'
            )

    plt.tight_layout()
    plt.savefig('Ankieta_05_Wybory_Utwory.png', dpi=300)
    plt.close()
    print("Wygenerowano wykres 05: Preferencje wyboru modelu w zależności od utworu")


if __name__ == "__main__":
    nazwa_pliku = "Badanie estetyki i spójności proceduralnie generowanych modeli terenu na podstawie dźwięku (Odpowiedzi).xlsx"
    if os.path.exists(nazwa_pliku):
        analizuj_ankiete(nazwa_pliku)
        print("Zakończono analizę ankiety pomyślnie!")
    else:
        print(f"Błąd: Nie znaleziono pliku '{nazwa_pliku}' w bieżącym folderze.")