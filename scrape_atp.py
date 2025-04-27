import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from db import insert_tournament, insert_player, insert_match, insert_match_stats

options = uc.ChromeOptions()
options.headless = False
driver = uc.Chrome(options=options)

wait = WebDriverWait(driver, 20)

driver.get("https://www.atptour.com/en/scores/results-archive?year=2025")
time.sleep(random.uniform(2, 4))

tournament_elements = wait.until(EC.presence_of_all_elements_located(
    (By.CSS_SELECTOR, "ul.events > li")
))

second_tournament = tournament_elements[1]

tournament_name = second_tournament.find_element(By.CSS_SELECTOR, "a.tournament__profile").text
city = "Dummy City"
year = 2025

# tournament_id = insert_tournament(tournament_name, city, year)
# print(f"Tournament inserted with ID: {tournament_id}")

result_link = second_tournament.find_element(By.CSS_SELECTOR, ".non-live-cta a")
result_url = result_link.get_attribute("href")
print(f"Results URL: {result_url}")

driver.get(result_url)
time.sleep(random.uniform(2, 4))


matches = wait.until(EC.presence_of_all_elements_located(
    (By.CSS_SELECTOR, "div.match")
))
first_match = matches[4]

match_stats_link = first_match.find_element(By.CSS_SELECTOR, "div.match-cta a[href*='/scores/stats-centre/']")
stats_url = match_stats_link.get_attribute("href")
print(f"Stats URL: {stats_url}")

driver.get(stats_url)
time.sleep(random.uniform(2, 4))

stats = {}

stat_sections = wait.until(EC.presence_of_all_elements_located(
    (By.CSS_SELECTOR, "div.statTileWrapper")
))

for section in stat_sections:
    try:
        label_element = section.find_element(By.CSS_SELECTOR, "div.labelBold")
        label = label_element.text.strip().replace(" ", "_").upper()

        player1_stat = section.find_element(By.CSS_SELECTOR, "div.statWrapper.unclickable-stats.p1Stats").text.strip()
        player2_stat = section.find_element(By.CSS_SELECTOR, "div.statWrapper.unclickable-stats.p2Stats").text.strip()

        stats[label] = {
            "Player 1": player1_stat,
            "Player 2": player2_stat,
        }
    except Exception as e:
        print(f"Skipping one stat block because of: {e}")

player1_name = "Player 1"
player2_name = "Player 2"
player1_country = "Country"
player2_country = "Country"
player1_ranking = 1
player2_ranking = 2

player1_id = insert_player(player1_name, player1_country, player1_ranking)
player2_id = insert_player(player2_name, player2_country, player2_ranking)

match_stage = "Quarterfinal"
match_winner_id = player1_id
match_id = insert_match(1, match_stage, player1_id, player2_id, match_winner_id)

insert_match_stats(match_id, player1_id, stats, "Player 1")
insert_match_stats(match_id, player2_id, stats, "Player 2")

time.sleep(2)
driver.close()
driver.quit()
