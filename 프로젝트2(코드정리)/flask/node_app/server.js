const express = require('express');
const bodyParser = require('body-parser');

const app = express();
app.use(bodyParser.json());

app.post('/get-token', async (req, res) => {
    const code = req.body.code;
    const tokenUrl = 'https://kauth.kakao.com/oauth/token';
    const data = {
        grant_type: 'authorization_code',
        client_id: '1a32cc25cda2d539a52cbe6823886114a', // 카카오 앱의 REST API 키
        redirect_uri: 'http://localhost:8000/oauth', // 실제 서비스의 리다이렉트 URI
        code: code
    };

    // "node-fetch" 모듈을 동적으로 가져오기
    import('node-fetch').then(async fetch => {
        const response = await fetch.default(tokenUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams(data)
        });

        const tokenData = await response.json();
        res.json(tokenData);
    }).catch(error => {
        console.error('Error while dynamically importing node-fetch:', error);
        res.status(500).json({ error: 'Internal Server Error' });
    });
});

app.listen(8000, () => {
    console.log('Server running on http://localhost:8000');
});
