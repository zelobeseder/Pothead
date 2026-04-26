# Pothead
Hell modulator

**POT HEAD** — это система для конструирования и визуализации сложных многопроцессных взаимодействий. Инструмент позволяет:

- **Определять процессы** с параметрами (время жизни, масса, приоритет, зависимости)
- **Расчитывать оптимальные расписания** на основе фазовых взаимодействий
- **Визуализировать конфликты** — места где процессы конкурируют за ресурсы или временное окно
- **Экспортировать схемы взаимодействий** для анализа и презентации

## Текущий функционал (v1)

### Ядро системы

**Процессы** — каждый имеет:
- Имя и уникальный идентификатор
- `life` — длительность выполнения
- `mass` — требуемые ресурсы/вес
- `start` — когда включается в цикл
- `urgency` — приоритет выполнения
- `color` — визуальная идентификация

**Расчёты** включают:
- Peak load (максимальное одновременное потребление ресурсов)
- Mean load (средняя нагрузка)
- Conflict zones (периоды перекрытия высокоприоритетных процессов)
- Resource optimization (предложения по перепланированию)

### Визуализация

График с синусоидальными паттернами показывает:
- **Волны процессов** (каждый цвет = процесс)
- **Зоны пересечения** = стрессовые точки системы
- **Пустые промежутки** = окна для добавления новых процессов

## Применение

Идеально для:
- **Производства** — оркестрация кулинарных/мануфактурных циклов
- **Сценарного анализа** — управление сложными взаимодействиями персонажей/событий
- **Любых параллельных систем** с временными зависимостями и конфликтами ресурсов

## Архитектура

- **processes.py** — ядро: расчёты, конфликты, оптимизация
- **processes-lib.txt** — библиотека предустановленных процессов
- **GUI (POT HEAD)** — визуальный редактор и планировщик
- **Экспорт** — графики взаимодействий для документации

## Видение

Система, которая помогает **режиссёру/продюсеру/шефу/менеджеру0** увидеть скрытые конфликты в сложных системах и найти элегантные решения для их разрешения.


Research Summary: Preparation Processes for Professional Hot Line

Overview

This project aims to assemble a comprehensive library of long-duration cooking processes for a professional kitchen.  The goal is to provide realistic life (total duration) and active (hands‑on involvement) times for various stocks, broths, sauces, soups, stews, braises, roasts and other preparatory tasks.  Understanding how much attention each process demands helps chefs schedule their workflow and manage the “gravity” (attention load) of multiple tasks simultaneously.

Method

To determine realistic durations and hands‑on involvement, I searched for credible recipes and culinary guides published between 2024 – 2026.  These sources include professional chefs, culinary authors and well‑known cooking websites.  For each category of process I looked for information about total simmering/braising/roasting time and any notes on how actively the cook must stir, skim or monitor the food.  Where the sources provided minimum and maximum times, I used the ranges to inform the life times.  When the sources stressed frequent stirring or constant whisking, I treated the process as highly active; where they noted long simmering or braising with occasional skimming or stirring, I treated the process as low active.  The resulting 150‑item dataset reflects these findings.

Key Findings from Sources

Stocks and Broths
	•	Chicken and beef stock – Culinary instructor Kathleen Flinn notes that once a chicken stock comes to a boil, it should simmer uncovered for at least four hours, while beef stock needs at least eight hours; she mentions simmering her stocks for twelve hours and recommends skimming foam and fat every 90 minutes .  Vegetable stock, however, simmers for only about 40 minutes .  These times were used for the long chicken and beef stock processes, while vegetable stock and other quick stocks use shorter life times.
	•	Fish stock / seafood fumet – A professional fish stock recipe simmers the bones and aromatics for 30 minutes and then steeps them off the heat for 10 minutes .  This informed the 40‑minute life and modest active time for fish stock and seafood fumet in the dataset.
	•	Demi‑glace and espagnole sauce – A demi‑glace recipe caramelizes vegetables and deglazes with wine before simmering veal stock and reducing it over two hours with skimming every 15–20 minutes  .  Chef Billy Parisi’s espagnole sauce simmers for two hours with periodic skimming and includes a 20–25 minute roux preparation .  These sources justify long life times and moderate active involvement for demi‑glace and espagnole‐style processes.
	•	Velouté sauce – Chef Billy Parisi notes that velouté requires bringing stock and roux to a boil and then simmering over low heat for about 30 minutes , mostly hands‑off once the roux is made.

Sauces requiring constant attention
	•	Béchamel and Mornay – A béchamel recipe instructs to whisk melted butter and flour for 1–2 minutes and then cook the sauce for 10–15 minutes, stirring constantly until it thickens .  Mornay sauce (béchamel enriched with cheese) “comes together in 10 minutes” and requires continuous whisking to achieve a smooth texture .  These processes therefore have life times around 10–15 minutes and very high active ratios.
	•	Hollandaise and beurre blanc – Traditional hollandaise preparation uses a double boiler and demands 10–15 minutes of vigorous whisking .  Beurre blanc (white wine butter sauce) is “simple to prepare in about 15 minutes,” but again involves reducing wine and whisking in butter .  Both sauces are fully active and therefore have high urgency.
	•	Brown butter / beurre noisette – An article on sage brown butter sauce notes that browning butter takes about 4–5 minutes of swirling the pan, and the entire sauce “takes 10 minutes or less”  .  This informed the short life and high active time for brown‑butter‑based sauces.

Soups and Stews
	•	Cream of mushroom soup – A recipe instructs to simmer the soup after adding broth for about 20 minutes to thicken and infuse flavors .  I included additional time for sautéing the mushrooms and aromatics, resulting in a 40‑minute life and moderate active time.
	•	Beef stew – Valerie’s Kitchen simmered beef stew for 1½ hours, then added vegetables and simmered another 30–40 minutes  .  This yields a total simmer of around two hours, with occasional stirring; I used a similar life and active time for beef stew and other long stews.
	•	Fish / seafood stews – Fish stew and chowders typically cook for 45–60 minutes.  For instance, fish stock simmers for 30 minutes , and chowders often call for simmering after sautéing vegetables; I therefore set fish stew, clam and corn chowders to 50–60 minutes.
	•	Gumbo and goulash – Gumbo requires building a dark roux (often 20–25 minutes) and simmering the stew for two hours , so I set gumbo’s life to 150 minutes with significant active time.  Beef goulash and chili con carne similarly involve long, slow simmering with periodic stirring.
	•	Ramen and pho broths – Traditional ramen broth simmers for many hours; I assigned 240 minutes for ramen and 360 minutes for beef pho broth, with low active involvement.  These times reflect how professional kitchens prepare rich broths.

Braises and Roasts
	•	Braised lamb shanks – Chef Billy Parisi sears lamb shanks, deglazes, then bakes them covered in the oven at 350 °F for 2–2½ hours .  I used 150 minutes life for braised lamb shanks and similar braises like braised short ribs and oxtail.
	•	Short ribs and other braises – Oven‑braised short ribs cook covered for 3–3½ hours until fork‑tender .  Pot roasts, brisket, and other braises were assigned 180–240 minutes depending on the cut.
	•	Roasts and baked dishes – An easy roast chicken recipe roasts a 1.5–2 kg chicken at 180 °C (350 °F) for 1 hour 20 to 1 hour 30 minutes .  Similar times apply to roast pork loin, roast beef and roast leg of lamb.  Roasted vegetables such as root vegetables, carrots and Brussels sprouts typically roast at 425 °F for around 30 minutes  , so I assigned 30–45 minutes life and low active time for these.

Quick Preparations and Miscellaneous Tasks

Many processes on a hot line are shorter but still require focus.  Pasta cooking, sautéing, searing and blanching are highly active despite their brevity.  For example, dry pasta generally cooks in 8–12 minutes  , and fresh pasta can cook in just 1–3 minutes .  Making a roux, browning butter, clarifying butter and caramelizing sugar are all under 15 minutes but demand constant attention; these were assigned high active times and urgency in the dataset.  Caramelizing onions is slower—it takes 25–45 minutes and requires regular stirring  , so I set the life to 40 minutes with 20 minutes active involvement.

Dataset Construction

Using the above research and typical professional practice, I created a file processes_import.txt containing 150 unique processes formatted for the Constructor’s import feature.  Each line includes the process name, total life in minutes, active time expressed as minutes (and ticks if necessary), an urgency value (0.0 = low, 0.5 = medium, 1.0 = high) and a randomly generated HEX color for UI visualization.  Processes with high ratios of active/life time (e.g., sauces like hollandaise, béchamel, roux) were given high urgency; long simmering stocks and braises received low urgency.

Distribution
	•	Total processes: 150
	•	Processes with life < 15 minutes: 20 (~13 %), satisfying the requirement that quick tasks remain under 30 % of the dataset.
	•	Oven‑based (roasts & baked braises): 30 processes include roasted meats, vegetables and baked braises.
	•	Stove‑top (sauces, stocks, soups, stews and other preparations): 120 processes.

Conclusion

By consulting authoritative culinary sources for timings and attention requirements, I compiled a large library of processes reflecting the “real gravity” of professional kitchen tasks.  The dataset balances long, low‑attention stock and braise preparations with shorter, high‑attention sauces and sautéing tasks, giving chefs realistic scheduling inputs for a hot‑line environment.
