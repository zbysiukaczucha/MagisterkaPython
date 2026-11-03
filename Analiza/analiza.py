import os
import warnings
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import imageio.v3 as iio
import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)

# ==========================================
# KONFIGURACJA ŚCIEŻEK
# ==========================================
FOLDER_CSV = r'C:\CSVs'
FOLDER_EXR = r'C:\Heightmaps'

# ==========================================
# 1. ANALIZA EXCELA (CZASY I KORELACJE)
# ==========================================
def analizuj_excel(df):
    print("Rozpoczynam analizę z pliku Excel (czasy, wydajność)...")

    plt.figure(figsize=(12, 7))
    if 'Kategoria' in df.columns:
        sns.scatterplot(x='Długość pliku [s]', y='Czas algorytmu [ms]', hue='Algorytm', style='Kategoria', s=150,
                        data=df, palette='Set1')
    else:
        sns.scatterplot(x='Długość pliku [s]', y='Czas algorytmu [ms]', hue='Algorytm', s=150, data=df, palette='Set1')

    plt.title('Zależność czasu generowania od długości pliku audio')
    plt.ylabel('Czas wykonywania algorytmu [ms]')
    plt.xlabel('Długość pliku audio [s]')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig('Wykres_EXCEL_Skalowalnosc_Czasowa.png', dpi=300)
    plt.close('all')

    # --- Wykres 1B: Czas algorytmu (Boxplot - tylko standardowe iteracje 360) ---
    if 'Kategoria' in df.columns:
        # Filtrujemy tylko jabłka do jabłek (baza 360 iteracji, Substepping On)
        df_base = df[(df['Liczba iteracji'] == 360) & (df['Substepping'] == 'On')]

        plt.figure(figsize=(12, 7))
        sns.boxplot(x='Kategoria', y='Czas algorytmu [ms]', hue='Algorytm', data=df_base, palette='Set2')
        plt.title('Rozkład czasu wykonywania algorytmów (baza: 360 iteracji, Substepping: On)')
        plt.ylabel('Czas wykonywania algorytmu [ms]')
        plt.xlabel('Kategoria pliku')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig('Wykres_EXCEL_Czas_Kategorie.png', dpi=300)
        plt.close('all')

    # --- Wykres 1C: Czas renderowania (Boxplot - standardowe iteracje 360) ---
    if 'Kategoria' in df.columns:
        plt.figure(figsize=(10, 6))
        sns.boxplot(x='Algorytm', y='Czas renderowania [s]', data=df_base, palette='Pastel1')
        plt.title(
            'Rozkład czasu renderowania zaktualizowanej mapy wysokości\n(baza: 360 iteracji, Substepping: On)')
        plt.ylabel('Czas renderowania [s]')
        plt.xlabel('Algorytm')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig('Wykres_EXCEL_Czas_Renderowania.png', dpi=300)
        plt.close('all')

    # --- Wykres 1D: Wpływ Substeppingu na czas renderowania (Testy brzegowe) ---
    if 'Substepping' in df.columns:
        # Wybieramy konkretne próbki brzegowe z iteracjami 360 do porównania
        df_sub = df[(df['Liczba iteracji'] == 360) &
                    (df['Plik audio'].isin(['GlassBreaking', 'Thunderstorm', 'Ambient', 'PunkRock']))]

        # Odrzucamy warianty bez pary (żeby wykres był czytelny)
        df_sub_filtered = df_sub.groupby('Plik audio').filter(lambda x: len(x['Substepping'].unique()) > 1)

        if not df_sub_filtered.empty:
            plt.figure(figsize=(10, 6))
            sns.barplot(x='Plik audio', y='Czas renderowania [s]', hue='Substepping', data=df_sub_filtered,
                        palette='Set1')
            plt.title('Wpływ mechanizmu Substepping na czas renderowania')
            plt.ylabel('Czas renderowania [s]')
            plt.xlabel('Plik audio (Wybrane testy brzegowe)')
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            plt.legend(title='Substepping')
            plt.tight_layout()
            plt.savefig('Wykres_EXCEL_Substepping_Renderowanie.png', dpi=300)
            plt.close('all')

    print("\n--- STATYSTYKI Z EXCELA ---")
    cols_num = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(cols_num) > 1:
        corr_matrix = df[cols_num].corr()
        print("Macierz korelacji (Współczynnik Pearsona):")
        print(corr_matrix)

        plt.figure(figsize=(8, 6))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", vmin=-1, vmax=1)
        plt.title('Macierz korelacji parametrów wydajnościowych')
        plt.tight_layout()
        plt.savefig('Wykres_EXCEL_Korelacja.png', dpi=300)
        plt.close('all')


# ==========================================
# 2. ANALIZA PLIKÓW CSV (KĄTY, NAVMESH, Z, STATYSTYKI)
# ==========================================
def analizuj_csv():
    print("\nRozpoczynam zautomatyzowaną analizę plików CSV...")
    folder_csv = FOLDER_CSV

    pliki_csv = [f for f in os.listdir(folder_csv) if f.endswith('.csv') and '_' in f]

    if not pliki_csv:
        print("Brak plików CSV do przetworzenia.")
        return pd.DataFrame()

    # exist_ok=True zapobiega błędom, jeśli folder już istnieje
    os.makedirs('Wyniki_CSV', exist_ok=True)

    wyniki = []

    for plik in pliki_csv:
        try:
            nazwa_bez_ext = plik.rsplit('.', 1)[0]
            # Czyszczenie nazwy z potencjalnych błędnych znaków z Windowsa
            safe_name = re.sub(r'[\\/*?:"<>|\n\r\t]', "", nazwa_bez_ext.strip())

            czesci = safe_name.split('_')

            audio = czesci[0]
            algorytm = czesci[1] if len(czesci) > 1 else "Nieznany"
            iteracje = int(czesci[2]) if len(czesci) > 2 and czesci[2].isdigit() else 360
            sub = czesci[3] if len(czesci) > 3 else "On"

            pelna_sciezka = os.path.join(folder_csv, plik)
            df_csv = pd.read_csv(pelna_sciezka)

            df_csv.columns = df_csv.columns.str.strip()

            min_z = df_csv['Z'].min()
            max_z = df_csv['Z'].max()
            var_z = df_csv['Z'].var()

            navmesh_pct = (df_csv['Navmesh'].mean()) * 100

            mean_angle = df_csv['Angle'].mean()
            max_angle = df_csv['Angle'].max()
            var_angle = df_csv['Angle'].var()

            wyniki.append({
                'Plik': safe_name,
                'Audio': audio,
                'Algorytm': algorytm,
                'Iteracje': iteracje,
                'Substepping': sub,
                'Min Z': min_z,
                'Max Z': max_z,
                'Wariancja Z': var_z,
                'NavMesh [%]': navmesh_pct,
                'Sredni Kat': mean_angle,
                'Max Kat': max_angle,
                'Wariancja Katu': var_angle
            })

            plt.figure(figsize=(8, 5))
            sns.histplot(df_csv['Angle'], bins=50, kde=True, color='darkorange')
            plt.title(f'Rozkład kątów nachylenia\n({safe_name})')
            plt.xlabel('Kąt nachylenia [stopnie]')
            plt.ylabel('Liczba punktów wierzchołków')
            plt.axvline(mean_angle, color='red', linestyle='dashed', linewidth=2, label=f'Średnia: {mean_angle:.1f}°')
            plt.legend()
            plt.grid(True, linestyle='--', alpha=0.5)
            plt.tight_layout()

            # Bezpieczne zapisywanie pliku
            sciezka_wykresu = os.path.join('Wyniki_CSV', f'{safe_name}_Katy.png')
            plt.savefig(sciezka_wykresu, dpi=300)
            plt.close('all')

        except Exception as e:
            print(f"Błąd przetwarzania CSV {plik}: {e}")

    df_wyniki = pd.DataFrame(wyniki)

    if 'Iteracje' in df_wyniki.columns and len(df_wyniki['Iteracje'].unique()) > 1:
        plt.figure(figsize=(10, 6))
        sns.barplot(x='Audio', y='NavMesh [%]', hue='Iteracje', data=df_wyniki, palette='crest')
        plt.title('Wpływ liczby iteracji algorytmu na grywalną powierzchnię (NavMesh)')
        plt.ylabel('NavMesh [%]')
        plt.xlabel('Plik audio')
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.legend(title="Liczba Iteracji")
        plt.tight_layout()
        plt.savefig(os.path.join('Wyniki_CSV', 'Porownanie_Brzegowe_Iteracje_NavMesh.png'), dpi=300)
        plt.close('all')

    if 'Substepping' in df_wyniki.columns and len(df_wyniki['Substepping'].unique()) > 1:
        df_sub = df_wyniki[df_wyniki['Iteracje'] == 360]
        if not df_sub.empty:
            plt.figure(figsize=(10, 6))
            sns.barplot(x='Audio', y='Max Z', hue='Substepping', data=df_sub, palette='flare')
            plt.title('Wpływ mechanizmu Substepping na stabilność rzutowania (Max Z)')
            plt.ylabel('Maksymalna wysokość Z [Unreal Units]')
            plt.xlabel('Plik audio')
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            plt.legend(title="Substepping")
            plt.tight_layout()
            plt.savefig(os.path.join('Wyniki_CSV', 'Porownanie_Brzegowe_Substepping_MaxZ.png'), dpi=300)
            plt.close('all')

    # ==========================================
    # DODATKOWE WYKRESY Z ZAGREGOWANYCH DANYCH TOPOLOGICZNYCH
    # ==========================================

    # 3. Wpływ średniego kąta na grywalność terenu (Regresja)
    if 'Sredni Kat' in df_wyniki.columns and 'NavMesh [%]' in df_wyniki.columns:
        plt.figure(figsize=(10, 6))
        sns.regplot(x='Sredni Kat', y='NavMesh [%]', data=df_wyniki, scatter_kws={'s': 100, 'alpha': 0.7},
                    color='purple', line_kws={'color': 'red'})
        plt.title('Korelacja między średnim nachyleniem terenu a jego grywalnością')
        plt.xlabel('Średni kąt nachylenia terenu [stopnie]')
        plt.ylabel('Grywalna powierzchnia (NavMesh) [%]')
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        plt.savefig(os.path.join('Wyniki_CSV', 'Korelacja_Kat_vs_NavMesh.png'), dpi=300)
        plt.close('all')

    # 4. Wariancja kątów (Poszarpanie terenu) dla różnych algorytmów
    df_base = df_wyniki[df_wyniki['Iteracje'] == 360]
    if not df_base.empty and 'Wariancja Katu' in df_base.columns:
        plt.figure(figsize=(10, 6))
        # NAPRAWA FUTURE WARNING: dodano hue='Algorytm' i legend=False
        sns.boxplot(x='Algorytm', y='Wariancja Katu', data=df_base, hue='Algorytm', legend=False, palette='Set2')
        sns.stripplot(x='Algorytm', y='Wariancja Katu', data=df_base, hue='Algorytm', legend=False, color='black',
                      size=6, alpha=0.6)
        plt.title('Zróżnicowanie nachylenia terenu (Wariancja kątów) wg algorytmu')
        plt.ylabel('Wariancja kątów nachylenia')
        plt.xlabel('Algorytm')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(os.path.join('Wyniki_CSV', 'Boxplot_Wariancja_Katow.png'), dpi=300)
        plt.close('all')

    print("Zakończono analizę CSV. Wyniki zapisano w tabeli df_wyniki.")
    df_wyniki.to_csv('Zbiorcze_Wyniki_Topologii.csv', index=False)

    return df_wyniki


# ==========================================
# 3. ANALIZA EXR Z KALIBRACJĄ NA BAZIE CSV
# ==========================================
def analizuj_exr(df_stats):
    print("\nRozpoczynam analizę plików EXR (kalibracja osi Z na podstawie wyników z CSV)...")
    folder_exr = FOLDER_EXR

    pliki_exr = [f for f in os.listdir(folder_exr) if f.lower().endswith('.exr')]

    if not pliki_exr:
        print("Brak plików EXR do przetworzenia.")
        return

    os.makedirs('Wyniki_EXR', exist_ok=True)

    for plik in pliki_exr:
        nazwa_bez_ext = plik.rsplit('.', 1)[0]
        safe_name = re.sub(r'[\\/*?:"<>|\n\r\t]', "", nazwa_bez_ext.strip())
        fig = None

        try:
            pelna_sciezka_exr = os.path.join(folder_exr, plik)
            img = iio.imread(pelna_sciezka_exr, plugin="pyav")
            img = np.squeeze(img)

            if len(img.shape) == 3:
                img_gray = img[:, :, 0]
            else:
                img_gray = img

            prawdziwe_min, prawdziwe_max = 0, 1
            if not df_stats.empty and safe_name in df_stats['Plik'].values:
                wiersz = df_stats[df_stats['Plik'] == safe_name].iloc[0]
                prawdziwe_min = wiersz['Min Z']
                prawdziwe_max = wiersz['Max Z']

                img_min = img_gray.min()
                img_max = img_gray.max()

                if img_max > img_min:
                    img_norm = (img_gray - img_min) / (img_max - img_min)
                    img_gray = img_norm * (prawdziwe_max - prawdziwe_min) + prawdziwe_min
                else:
                    img_gray = np.full(img_gray.shape, prawdziwe_min)
            else:
                print(f"  [Uwaga] Brak pliku CSV dla '{safe_name}'. Mapa będzie nieskalowana.")

            if "Silence" not in safe_name:
                dane_1d = img_gray[img_gray > img_gray.min() + 0.01].flatten()
                if len(dane_1d) == 0:
                    dane_1d = img_gray.flatten()
            else:
                dane_1d = img_gray.flatten()

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

            im = ax1.imshow(img_gray, cmap='terrain')
            ax1.set_title(f'Mapa Wysokości: {safe_name}')
            fig.colorbar(im, ax=ax1, label='Wysokość [Unreal Units]')

            ax2.hist(dane_1d, bins=100, color='royalblue', alpha=0.7, edgecolor='black')
            ax2.set_title('Histogram dystrybucji wysokości (Hipsometria)')
            ax2.set_xlabel('Wysokość [Unreal Units]')
            ax2.set_ylabel('Liczba pikseli')
            ax2.grid(True, linestyle='--', alpha=0.5)

            plt.tight_layout()
            sciezka_wykresu_exr = os.path.join('Wyniki_EXR', f'{safe_name}_Analiza.png')
            plt.savefig(sciezka_wykresu_exr, dpi=300)
            plt.close('all')

        except Exception as e:
            print(f"Błąd przy pliku {plik}: {e}")
        finally:
            if fig is not None:
                plt.close(fig)


if __name__ == "__main__":
    plik_excel = "BadaniaMagisterka.xlsx"

    if os.path.exists(plik_excel):
        print(f"Wczytywanie bazy danych wydajnościowych: {plik_excel}...")
        try:
            dane_excel = pd.read_excel(plik_excel)
            analizuj_excel(dane_excel)
        except Exception as e:
            print(f"Błąd odczytu Excela: {e}")
    else:
        print(f"Brak pliku {plik_excel}. Pomijam generowanie wykresów czasowych.")

    df_statystyki_csv = analizuj_csv()

    if not df_statystyki_csv.empty:
        analizuj_exr(df_statystyki_csv)
    else:
        print("Nie wykonano analizy EXR, ponieważ brakuje statystyk z plików CSV do prawidłowego skalowania osi Z.")

    print("\nCałkowicie zakończono działanie skryptu! Wyniki znajdziesz w folderach Wyniki_CSV oraz Wyniki_EXR.")