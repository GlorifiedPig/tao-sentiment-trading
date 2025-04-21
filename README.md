# Bittensor Sentiment-Based Staking

This is a demonstration project that analyzes Twitter sentiment regarding Bittensor networks and automatically stakes Tao coins based on the sentiment analysis. The project uses datura.ai and chutes.ai to analyze tweets and make trading decisions.

It exposes an API endpoint, which connects to datura.ai to fetch the latest tweets regarding a chosen netuid, and then connects to chutes.ai to analyze sentiment.

Based off this score (ranging from -100 to 100), we multiply that by * 0.01, and use the Bittensor libraries to stake or unstake that amount of Tao on that netuid depending on if we have a positive or negative sentiment.

This is all done on the test network.

## Prerequisites

- Docker
- Git
- A Bittensor Wallet

## Demonstration Video
[You can find a demonstration video here](https://www.youtube.com/watch?v=dA7x4oWuc20)

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/GlorifiedPig/tao-sentiment-trading.git
cd tao-sentiment-trading
```

### 2. Environment Configuration

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

Edit the `.env` file and fill in the required environment variables:

#### API Keys
- `DATURA_API_KEY`: Your API key from [Datura.ai](https://datura.ai) for Twitter data access
- `CHUTES_API_KEY`: Your API key from [Chutes.ai](https://chutes.ai) for sentiment analysis

#### Wallet Configuration
- `WALLET_NAME`: Your Bittensor wallet name
- `WALLET_HOTKEY`: Your Bittensor wallet hotkey

#### Database Configuration
The default MySQL configuration is:
```
MYSQL_HOST=mysql
MYSQL_USER=tao
MYSQL_PASSWORD=tao
MYSQL_DATABASE=tao
```

#### Redis Configuration
The default Redis configuration is:
```
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
```

### 3. Wallet Setup

Copy your Bittensor wallet files to the project's wallets directory:

```bash
# Create the wallets directory if it doesn't exist
mkdir -p wallets

# Copy your wallet files from the default Bittensor location
cp -r ~/.bittensor/wallets/* ./wallets/
```

Make sure the wallet files have the correct permissions and the docker container has access to them.

**Please make sure your wallet is not password protected.**

### 4. Start the Services

Build and start the Docker containers:

```bash
docker compose up --build
```

### 5. Access the API

Once the services are running, you can access:
- API Documentation: http://localhost:8000/api/v1/docs
- Endpoint for trading: http://localhost:8000/api/v1/tao_dividends

## API Authentication

The API uses OAuth2. Default credentials:
- Username: `admin`
- Password: `admin`

Make a POST request to `http://localhost:8000/api/v1/token` to get the Bearer token.

It is hard coded to `fake-token`, so you could also just add the `Authorization: Bearer fake-token` header to all requests.
