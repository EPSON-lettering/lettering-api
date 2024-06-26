DO $$
    DECLARE
        p_user_id INT;
        p_match_id INT;
    BEGIN

        DELETE FROM oauth_oauthuser oauth
        WHERE oauth.provider_id = 'deveungi@gmail.com'; # 이부분 수정해주세요


        SELECT u.id INTO p_user_id
        FROM accounts_user u
        WHERE u.nickname = '아직도내가은기로보여' # 이부분 수정해주세요
        LIMIT 1;

        SELECT m.id INTO p_match_id
        FROM matching_match as m
        WHERE m.requester_id = p_user_id or m.acceptor_id = p_user_id
        ORDER BY m.created_at DESC
        LIMIT 1;

        RAISE NOTICE 'match id: %', p_match_id;

        DELETE FROM matching_match_provided_questions as pq
        WHERE pq.match_id = p_match_id;

        DELETE FROM matching_match as m
        WHERE m.id = p_match_id or m.requester_id = p_user_id or m.acceptor_id = p_user_id;

        DELETE FROM matching_matchrequest mr
        WHERE mr.requester_id = p_user_id or mr.receiver_id = p_user_id;

        DELETE FROM interests_userinterest ui
        WHERE ui.user_id = p_user_id;

        DELETE FROM token_blacklist_outstandingtoken out_t
        WHERE out_t.user_id = p_user_id;

        DELETE FROM accounts_user u
        WHERE u.id = p_user_id;

        RAISE NOTICE '% 번 사용자 데이터가 완전히 제거되었습니다.', p_user_id;
END $$;
