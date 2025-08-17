from db_utils import get_all_detected_posts, insert_new_posts
from scrapping import login_instagram_and_navigate_to_profile, scroll_searching_new_posts



if __name__ == '__main__':
    driver = login_instagram_and_navigate_to_profile("atractive_smithers")
    detected_posts = get_all_detected_posts()
    new_post_ids = scroll_searching_new_posts(
        driver,
        already_detected_posts=detected_posts,
        total_allowed_duplicated_posts=1000)
    insert_new_posts(new_post_ids)
