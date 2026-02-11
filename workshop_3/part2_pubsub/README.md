# Part 2: Publisher-Subscriber with Multiple Services

## Description
This implementation provides a Publisher-Subscriber pattern using ZeroMQ with multiple publishers offering different services and subscribers that can subscribe to multiple publishers simultaneously.

## Files
- `publisher.py` - Multi-service publisher (WEATHER, NEWS, SPORTS, FINANCE)
- `subscriber.py` - Multi-subscription subscriber

## Available Services

1. **WEATHER** (Port 15001)
   - Temperature updates
   - Weather conditions

2. **NEWS** (Port 15002)
   - Breaking news from different topics
   - Politics, Technology, Science, World

3. **SPORTS** (Port 15003)
   - Live game scores
   - Team matchups

4. **FINANCE** (Port 15004)
   - Stock prices
   - Market changes

## Usage

### Local Testing (Same Machine)

1. **Start multiple publishers (each in a separate terminal):**
```bash
python publisher.py WEATHER
python publisher.py NEWS
python publisher.py SPORTS
python publisher.py FINANCE
```

2. **Start subscribers with different subscriptions:**

**Subscriber 1** (subscribes to WEATHER only):
```bash
python subscriber.py WEATHER
```

**Subscriber 2** (subscribes to NEWS and SPORTS):
```bash
python subscriber.py NEWS SPORTS
```

**Subscriber 3** (subscribes to all services):
```bash
python subscriber.py WEATHER NEWS SPORTS FINANCE
```

### Testing on Different Hosts

1. **On publisher machines:**
   - Edit `publisher.py` line 24: Change `HOST = 'localhost'` to `HOST = '0.0.0.0'`
   - Run publishers: `python publisher.py <SERVICE_TYPE>`

2. **On subscriber machines:**
   - Edit `subscriber.py` line 23: Change `HOST = 'localhost'` to publisher's IP address
   - Run subscriber: `python subscriber.py <SERVICE1> [SERVICE2] ...`

### Testing with Multiple Subscribers

Run multiple subscriber instances simultaneously:

**Terminal 1:**
```bash
python subscriber.py WEATHER FINANCE
```

**Terminal 2:**
```bash
python subscriber.py NEWS SPORTS
```

**Terminal 3:**
```bash
python subscriber.py WEATHER NEWS SPORTS FINANCE
```

All subscribers will receive messages from their subscribed services independently.

## Example Output

**Publisher (WEATHER):**
```
Publisher started for WEATHER service on tcp://localhost:15001
Publishing messages every 3 seconds...
[1] Published: WEATHER [14:30:15] Temperature: 25°C, Condition: Sunny
[2] Published: WEATHER [14:30:18] Temperature: 22°C, Condition: Cloudy
```

**Subscriber (subscribed to WEATHER and NEWS):**
```
Subscribing to services: WEATHER, NEWS
Connected to WEATHER service at tcp://localhost:15001
Connected to NEWS service at tcp://localhost:15002
Receiving messages...
[1] WEATHER [14:30:15] Temperature: 25°C, Condition: Sunny
[2] NEWS [14:30:16] Breaking news in Technology: Important event occurred
[3] WEATHER [14:30:18] Temperature: 22°C, Condition: Cloudy
```

## Architecture

- **Decoupled Communication**: Publishers don't know about subscribers
- **Multiple Publishers**: Each service runs on a different port
- **Flexible Subscriptions**: Subscribers can choose any combination of services
- **Topic-Based Filtering**: Messages filtered by service type prefix

## Requirements
- Python 3.x
- ZeroMQ library: `pip install pyzmq`
