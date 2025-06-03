import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from db import insert_tournament, insert_player, insert_match, insert_stats, Session, Player, engine
from sqlalchemy import select

options = uc.ChromeOptions()
options.headless = False
driver = uc.Chrome(options=options)
wait = WebDriverWait(driver, 20)


def open_and_wait(url):
    driver.get(url)
    time.sleep(random.uniform(2, 4))


def get_or_create_player(name: str, ranking: int = 0) -> int:
    with Session(engine) as session:
        statement = select(Player).where(Player.name == name)
        player = session.exec(statement).first()
        if player:
            player = player[0]
            return player.id
    return insert_player(name)


def normalize_stat_key(label: str) -> str:
    return label.strip().lower().replace(" ", "_")


def process_stat_value(val: str):
    val = val.strip()
    if '(' in val and '%' in val:
        try:
            perc = val[val.find('(') + 1 : val.find('%')].strip()
            return round(float(perc) / 100, 2)
        except:
            pass
    return int(val)


def scrape_stats_page(stats_url):
    open_and_wait(stats_url)

    stats = {
        "Player 1": {},
        "Player 2": {}
    }

    stat_sections = wait.until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, "div.statTileWrapper")
    ))

    for section in stat_sections:
        try:
            raw_label = section.find_element(By.CSS_SELECTOR, "div.labelWrappper > div").text
            label = normalize_stat_key(raw_label)
            p1_stat = section.find_element(By.CSS_SELECTOR, "div.p1Stats").text
            p2_stat = section.find_element(By.CSS_SELECTOR, "div.p2Stats").text

            stats["Player 1"][label] = process_stat_value(p1_stat)
            stats["Player 2"][label] = process_stat_value(p2_stat)
        except Exception as e:
            print(f"Skipped a stat block: {e}")
    return stats



def scrape_tournament_by_index(index, year=2025):
    open_and_wait(f"https://www.atptour.com/en/scores/results-archive?year={year}")

    tournament_elements = wait.until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, "ul.events > li")
    ))

    tournament_el = tournament_elements[index]

    name = tournament_el.find_element(By.CSS_SELECTOR, "a.tournament__profile").text.split('\n')[0]
    city = tournament_el.find_element(By.CSS_SELECTOR, "span.venue").text.strip(" |")
    tournament_id = insert_tournament(name, city, year)

    result_url = tournament_el.find_element(By.CSS_SELECTOR, ".non-live-cta a").get_attribute("href")
    open_and_wait(result_url)

    match_count = len(wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.match"))))

    for i in range(match_count):
        open_and_wait(result_url)
        matches = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.match")))
        match = matches[i]

        try:
            stats_link = match.find_element(By.CSS_SELECTOR, "div.match-cta a[href*='/scores/']")
            stats_url = stats_link.get_attribute("href")
            stats = scrape_stats_page(stats_url)

            player_elements = driver.find_elements(By.CSS_SELECTOR, "div.names a")
            p1_name = player_elements[0].text.strip()
            p2_name = player_elements[1].text.strip()
            p1_id = get_or_create_player(p1_name, 1)
            p2_id = get_or_create_player(p2_name, 2)
            winner_id = p1_id
            match_id = insert_match(tournament_id, p1_id, p2_id, winner_id)
            insert_stats(match_id, p1_id, stats["Player 1"])
            insert_stats(match_id, p2_id, stats["Player 2"])
            print(f"Inserted match: {p1_name} vs {p2_name}")
        except Exception as e:
            print("No statistics for this match")

        # except Exception as e:
        #     print(f"Skipped match {i+1}/{match_count} due to error: {e}")

    driver.quit()

if __name__ == "__main__":
    scrape_tournament_by_index(29)
