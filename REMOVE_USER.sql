DO $$
    DECLARE
        p_user_id INT;
        p_match_id INT;
    BEGIN
        SELECT u.id INTO p_user_id
        FROM accounts_user u
        WHERE u.nickname = '동현111' -- 이 부분 수정해주세요
        LIMIT 1;

        SELECT m.id INTO p_match_id
        FROM matching_match as m
        WHERE m.requester_id = p_user_id OR m.acceptor_id = p_user_id
        ORDER BY m.created_at DESC
        LIMIT 1;

        RAISE NOTICE 'match id: %', p_match_id;

        DELETE FROM matching_match_provided_questions
        WHERE match_id IN (
            SELECT id FROM matching_match
            WHERE requester_id = p_user_id OR acceptor_id = p_user_id
        );

        DELETE FROM matching_match
        WHERE id = p_match_id OR requester_id = p_user_id OR acceptor_id = p_user_id;

        DELETE FROM matching_matchrequest
        WHERE requester_id = p_user_id OR receiver_id = p_user_id;

        DELETE FROM interests_userinterest
        WHERE user_id = p_user_id;

        DELETE FROM token_blacklist_outstandingtoken
        WHERE user_id = p_user_id;

        DELETE FROM accounts_user
        WHERE id = p_user_id;

        DELETE FROM oauth_oauthuser
        WHERE provider_id = 'west.east1832@gmail.com'; -- 이 부분 수정해주세요

        RAISE NOTICE '% 번 사용자 데이터가 완전히 제거되었습니다.', p_user_id;
    END $$;
