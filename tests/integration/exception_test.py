import pytest

import stweet as st
from stweet.auth import TwitterAuthTokenProvider, SimpleAuthTokenProvider
from stweet.exceptions import RefreshTokenException, ScrapBatchBadResponse
from tests.integration.mock_web_client import MockWebClient


def test_get_auth_token_with_incorrect_response_1():
    with pytest.raises(RefreshTokenException):
        TwitterAuthTokenProvider(MockWebClient(None, None)).get_new_token()


def test_get_simple_auth_token_with_incorrect_response_1():
    with pytest.raises(RefreshTokenException):
        SimpleAuthTokenProvider(MockWebClient(None, None)).get_new_token()


def test_get_auth_token_with_incorrect_response_2():
    with pytest.raises(RefreshTokenException):
        TwitterAuthTokenProvider(MockWebClient(400, 'None')).get_new_token()


def test_get_auth_token_with_incorrect_response_3():
    with pytest.raises(RefreshTokenException):
        TwitterAuthTokenProvider(MockWebClient(200, 'None')).get_new_token()


def test_runner_exceptions():
    class TokenExpiryExceptionWebClient(st.WebClient):
        count_dict = dict({
            'https://twitter.com': 0,
            'https://api.twitter.com/2/search/adaptive.json': 0
        })

        def run_request(self, params: st.http_request.RequestDetails) -> st.http_request.RequestResponse:
            self.count_dict[params.url] = self.count_dict[params.url] + 1
            if params.url == 'https://api.twitter.com/2/search/adaptive.json':
                if self.count_dict[params.url] == 1:
                    return st.http_request.RequestResponse(429, None)
                else:
                    return st.http_request.RequestResponse(400, '')
            else:
                return st.http_request.RequestResponse(200, 'decodeURIComponent("gt=1330640566170869763; Max=10800;')

    with pytest.raises(ScrapBatchBadResponse):
        search_tweets_task = st.SearchTweetsTask(
            all_words='#koronawirus'
        )
        st.TweetSearchRunner(
            search_tweets_task=search_tweets_task,
            tweet_outputs=[],
            web_client=TokenExpiryExceptionWebClient(),
            auth_token_provider_factory=st.auth.TwitterAuthTokenProviderFactory()

        ).run()
