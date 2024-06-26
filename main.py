import itertools

import asyncio

from utils.create_files import create_files
from utils.user_menu import get_action
from utils.import_info import get_accounts_info
from utils.adjust_policy import set_windows_event_loop_policy
from data.config import TWITTER_TOKENS, PROXYS, PRIVATE_KEYS, EMAIL_DATA, logger
from settings.settings import ASYNC_SEMAPHORE
from db_api.database import initialize_db
from db_api.start_import import ImportToDB
from utils.create_task import (
    get_tokens_from_faucet,
    start_follow_and_retweet,
    check_token_balance,
    start_daily_galxe_mint,
    start_swaps,
    start_claim_galxe_activity_nft
)


def main():
    twitter_tokens: list[str] = get_accounts_info(TWITTER_TOKENS)
    proxies: list[str] = get_accounts_info(PROXYS)
    private_keys: list[str] = get_accounts_info(PRIVATE_KEYS)
    email_data: list[str] = get_accounts_info(EMAIL_DATA)

    cycled_proxies_list = itertools.cycle(proxies) if proxies else None

    logger.info(f'업로드 됨 в twitter_tokens.txt {len(twitter_tokens)} 계정 \n'
                f'\t\t\t\t\t\t\t업로드 됨 в proxys.txt {len(proxies)} 프록시 \n'
                f'\t\t\t\t\t\t\t업로드 됨 в private_keys.txt {len(private_keys)} 개인키 \n')

    formatted_data: list = [{
            'twitter_token': twitter_tokens.pop(0) if twitter_tokens else None,
            'proxy': next(cycled_proxies_list) if cycled_proxies_list else None,
            'private_key': private_key,
            'email_data': email_data.pop(0) if email_data else None
        } for private_key in private_keys
    ]

    user_choice = get_action()

    semaphore = asyncio.Semaphore(ASYNC_SEMAPHORE)

    if user_choice == '   1) 데이터베이스로 가져오기':

        asyncio.run(ImportToDB.add_account_to_db(accounts_data=formatted_data))

    elif user_choice == '   2) 수도꼭지에서 토큰 받기':

        asyncio.run(get_tokens_from_faucet(semaphore))

    elif user_choice == '   3) 다시 게시하고 구독하세요':

        asyncio.run(start_follow_and_retweet(semaphore))

    elif user_choice == '   4) 지갑 잔액 확인':

        asyncio.run(check_token_balance(semaphore))

    elif user_choice == '   5) 매일 galxe mint':

        asyncio.run(start_daily_galxe_mint(semaphore))

    elif user_choice == '   6) galxe의 기본 동작(온체인)':

        asyncio.run(start_swaps(semaphore))

    elif user_choice == '   7) Claim galxe 70 points':

        asyncio.run(start_claim_galxe_activity_nft(semaphore))

    elif user_choice == '   8) Claim galxe 50 points (트위터 없음)':

        asyncio.run(start_claim_galxe_activity_nft(semaphore, option=8))

    else:
        logger.error('잘못된 작업이 선택되었습니다.')


if __name__ == "__main__":
    try:
        asyncio.run(initialize_db())
        create_files()
        set_windows_event_loop_policy()
        main()
    except TypeError:
        logger.info('프로그램 완료')