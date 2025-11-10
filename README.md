# Clyst - Art Marketplace & Community Platform

Clyst is a comprehensive web application that serves as both a social platform for artists to share their work and a marketplace for selling artwork. Built with Flask and featuring AI-powered content generation, natural language search, and multilingual support.

## 🌟 Features

### Core Functionality
- **Community Feed**: Artists can share their artwork with the community through posts
- **Marketplace**: Buy and sell artwork with integrated pricing and product management
- **Shopping Cart**: Full-featured shopping cart with add, update quantity, and remove functionality
- **Order Management**: Complete e-commerce workflow from checkout to order tracking
- **Reviews & Ratings**: Interactive 1-5 star rating system integrated with product reviews
- **User Authentication**: Secure registration, login, and profile management with Flask-Login
- **Image Management**: Support for both URL-based and file upload images with secure handling
- **Search & Discovery**: Natural language search with price filtering and rating display
- **Portfolio Management**: AI-generated portfolio narratives for artist profiles
- **Promote Product to Post**: Turn a marketplace product into a community post with one click and a Promoted badge
- **Verification (Get Verified)**: Dedicated camera page to complete simple verification from profile
- **Likes & Comments**: Like posts and participate in discussions via comments (login required to like or comment; buttons visible to guests)
- **Artist Analytics Dashboard**: Comprehensive business intelligence dashboard for artists
  - Real-time KPI tracking (Views, Engagement, Sales, Revenue)
  - 30-day trend visualization with interactive charts
  - Sales analysis by product category
  - Top products and posts performance metrics
  - AI-powered business insights and recommendations
  - Competitive pricing analysis with market benchmarking

### AI-Powered Features
- **Content Generation**: AI-powered title and description suggestions for posts and products using Google Gemini
- **Multilingual Support**: Automatic translation of content into 15+ languages including Indian languages
- **SEO Optimization**: AI-generated SEO phrases for better discoverability
- **Image Analysis**: AI analyzes uploaded images to generate contextual content
- **Portfolio Narratives**: AI creates compelling stories connecting an artist's works
- **AI Business Insights**: Intelligent analysis of artist performance across products, marketing, pricing, and growth opportunities
- **Competitive Pricing Analysis**: AI-powered product similarity matching with market benchmarking and optional external market research (Amazon, Etsy, Flipkart)
- **Smart Analytics Dashboard**: Comprehensive analytics with KPIs, trends, sales by category, and AI-driven recommendations

### Advanced Search
- **Natural Language Processing**: Search using phrases like "minimalist monochrome abstracts under ₹5k"
- **Price Filtering**: Support for price ranges, minimum/maximum price constraints
- **Keyword Extraction**: Intelligent keyword parsing from search queries
- **Multi-field Search**: Search across titles, descriptions, and artist names
- **Currency Support**: Handles ₹, Rs, INR with k/M suffixes (e.g., "5k", "2M")

### User Experience
- **Responsive Design**: Mobile-first design with adaptive layouts
- **Accessibility**: Text-to-speech functionality for content
- **Modern UI**: Clean, Instagram-inspired interface with smooth animations
- **Real-time Features**: Dynamic content updates and interactive elements
- **File Upload Security**: Secure filename handling and type validation

## 🛠️ Technology Stack

### Backend
- **Flask 3.0.0**: Web framework
- **SQLAlchemy 2.0.38**: ORM for database operations
- **Flask-Login 0.6.3**: User authentication and session management
- **Flask-SQLAlchemy 3.1.1**: Flask integration with SQLAlchemy
- **Flask-Bootstrap5 0.1.dev1**: Bootstrap integration
- **Flask-CKEditor 1.0.0**: Rich text editor
- **Werkzeug 3.0.1**: WSGI toolkit with password hashing
- **python-dotenv 1.0.1**: Environment variable management
- **Groq API**: AI model integration for insights and competitive analysis (Llama 3.3 70B)

### Frontend
- **HTML5/CSS3**: Modern web standards with CSS Grid and Flexbox
- **JavaScript (ES6+)**: Interactive functionality and AJAX requests
- **Font Awesome 6.0.0**: Icon library
- **Responsive Design**: Mobile-first approach with adaptive layouts
- **CSS Variables**: Consistent theming and styling

### AI Integration
- **Google Gemini API**: AI content generation and translation
- **Groq API (Llama 3.3 70B)**: Advanced AI for business insights and competitive analysis
- **Natural Language Processing**: Custom search query parser
- **Image Analysis**: AI-powered image understanding
- **Multilingual Support**: 15+ languages including Indian languages
- **Business Intelligence**: AI-driven insights for product optimization, marketing strategy, pricing, and growth

### Database
- **SQLite**: Lightweight database for development
- **Database Migrations**: Managed via Flask-Migrate/Alembic for safe schema changes
- **File Storage**: Local file system with organized uploads

## 📁 Project Structure

```
ClystProto/
├── app.py                 # Main Flask application with all routes and models
├── config.py             # Configuration settings and API keys
├── natural_search.py     # Natural language search parser
├── ai.py                 # AI integration module for portfolio narratives
├── requirements.txt      # Python dependencies
├── .gitignore           # Git ignore rules
├── models/
│   └── dbs.py           # Database models (commented out - models in app.py)
├── templates/           # HTML templates
│   ├── index.html       # Community feed with search functionality
│   ├── products.html    # Marketplace with price filtering
│   ├── add_posts.html   # Create post form with AI suggestions
│   ├── add_products.html # Add product form with AI suggestions
│   ├── profile.html     # User profile with portfolio narrative
│   ├── analytics.html   # Analytics dashboard with AI insights
│   ├── login.html       # Login page
│   ├── register.html    # Registration page
│   └── product_buy.html # Product purchase page
├── static/
│   ├── css/
│   │   └── styles.css   # Global styles and common components
│   └── uploads/         # User uploaded files
│       ├── posts/       # Post images with UUID naming
│       └── products/    # Product images with UUID naming
└── instance/
   └── clyst.db        # SQLite database (dev DB lives here)
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ClystProto
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   - Edit `config.py` to set your API keys:
   ```python
   GEMINI_API_KEY = "your_gemini_api_key_here"
   FLASK_SECRET_KEY = "your_secret_key_here"
   GROQ_API_KEY = "your_groq_api_key_here"
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   - Open your browser and navigate to `http://localhost:5000`

## 🔧 Configuration

### API Keys Setup
1. **Google Gemini API**:
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Add it in `.env`

2. **Flask Secret Key**:
   - Generate a secure secret key for session management
   - Update it in `.env`

3. **GROQ API**:
   - Visit [Groq Console](https://console.groq.com/home)
   - Sign up and create a new API key
   - update it in `.env`


### Database Configuration
- The application uses SQLite by default
- Database file is created automatically in the `instance/` directory
- Tables are created on first run
- Migrations are available for evolving schemas
   - Initialize migrations (first time): `flask db init`
   - Generate migration: `flask db migrate -m "your message"`
   - Apply migration: `flask db upgrade`

## 📱 Usage Guide

### For Artists

1. **Registration & Profile**
   - Create an account with email, name, phone, and location
   - Access your profile to manage posts and products

2. **Creating Posts**
   - Share artwork with the community
   - Upload images or provide image URLs
   - Use AI to generate engaging titles and descriptions
   - Translate content into multiple languages
   - Promote a product to a post: From your profile, click "Promote Product" on a product; you'll be taken to Create Post with fields pre-filled. Submitting creates a post with a Promoted tag in the feed.

3. **Selling Products**
   - Add products to the marketplace
   - Set prices and detailed descriptions
   - Use AI suggestions for better product listings
   - Manage your product inventory

4. **Analytics Dashboard**
   - Access comprehensive analytics for your business
   - View key metrics: Views, Engagement, Items Sold, Revenue
   - Track performance with 30-day trend charts
   - Analyze sales by product category with visual bar charts
   - Get AI-powered business insights across 4 categories:
     - Product Optimization: Improve titles, descriptions, and images
     - Marketing Strategy: Enhance visibility and engagement
     - Pricing Strategy: Optimize pricing based on market analysis
     - Growth Opportunities: Discover new markets and trends
   - Competitive Pricing Analysis:
     - AI matches your products with similar items in the marketplace
     - Compare pricing against competitors based on product characteristics
     - Optional external market research (Amazon, Etsy, Flipkart)
     - Get similarity scores and reasons for product matching
     - Receive pricing recommendations and positioning advice

5. **Get Verified**
   - From your profile, click "Get verified now" to open the Camera page (`/camera`) and complete a simple verification step.

### Interacting with Posts (All Users)
- Like a post: Click the Like button on any post. If you’re not logged in, you’ll be prompted to log in first.
- View comments: Click the Comment button to expand or collapse the discussion for a post.
- Add a comment: When logged in, type your message in the reply box and submit. Guests see a "Login to comment" prompt.

Developer endpoints
- Get like count and state: `GET /api/post/<post_id>/likes`
- Toggle like: `POST /api/post/<post_id>/like`
- Add comment to post: `POST /comment/<post_id>` (form field: `comment`)
- Delete a post comment: `POST /comment/<comment_id>/delete`

### Analytics & AI Features

1. **Analytics Dashboard** (`/analytics`)
   - View comprehensive business metrics and insights
   - Access key performance indicators (KPIs)
   - Analyze trends with interactive charts
   - Review top-performing products and posts
   - Visualize sales by product category

2. **AI Business Insights** (`/analytics/insights`)
   - Automated analysis of your business performance
   - Four categories of actionable insights:
     - Product Optimization recommendations
     - Marketing strategy improvements
     - Pricing optimization suggestions
     - Growth opportunity identification
   - Real-time insights generated based on current data
   - Powered by Groq's Llama 3.3 70B model

3. **Competitive Pricing Analysis** (`/analytics/competitive-pricing`)
   - AI-powered similarity matching of products
   - Market price comparison and benchmarking
   - Optional external market research (`?external=true` query parameter)
   - Similarity scores with detailed reasoning
   - Pricing position analysis and recommendations
   - External pricing data from Amazon, Etsy, and Flipkart (when enabled)

### For Buyers

1. **Browsing & Discovery**
   - Explore the community feed for inspiration
   - Browse the marketplace with star ratings displayed on each product
   - Use natural language search (e.g., "abstract paintings under 5000")
   - View average ratings and review counts to make informed decisions

2. **Search Features**
   - Search by keywords, artist names, or descriptions
   - Filter by price ranges
   - Use phrases like "landscape oil painting below 7500"

3. **Shopping Cart**
   - Add products to cart with custom quantities
   - Update quantities or remove items from cart
   - View total price before checkout
   - Proceed to checkout for order placement

4. **Product Interaction**
   - View detailed product information with ratings
   - Leave reviews with 1-5 star ratings
   - Read other buyers' reviews and ratings
   - Rate and review products in one unified interface
   - Contact artists through their profiles
   - Use text-to-speech for accessibility

5. **Order Management**
   - Complete checkout process for cart items
   - Track order status (pending, completed, cancelled)
   - View order history with details and pricing

## 🔍 Search Capabilities

The application features an advanced natural language search system that understands:

### Price Queries
- `"under ₹5k"` - Maximum price filter
- `"above 2000"` - Minimum price filter
- `"between 1000 and 5000"` - Price range filter
- `"rs 1200"` - Exact price search
- `"less than 3k"` - Alternative syntax
- `"upto 7500"` - Maximum price constraint

### Style & Content Queries
- `"minimalist monochrome abstracts"` - Style-based search
- `"blue portrait"` - Color and subject search
- `"landscape oil painting"` - Medium and subject search
- `"abstract art"` - Genre-based search

### Combined Queries
- `"minimalist monochrome abstracts under ₹5k"` - Style + price
- `"blue portrait < 2000"` - Color + subject + price
- `"landscape painting between 2k and 8k"` - Subject + price range

### Currency Support
- Supports ₹, Rs, INR notations
- Handles k/M suffixes (5k = 5000, 2M = 2,000,000)
- Removes thousand separators (1,200 → 1200)

## ⭐ Reviews & Rating System

### Interactive Star Ratings
- **Modern Interface**: Clickable 1-5 star rating widget with hover effects
- **Unified Experience**: Rating integrated seamlessly with product reviews
- **Visual Feedback**: Active, hover, and selected states for better user experience
- **Rating Prefill**: Users can see and update their previous ratings

### Rating Features
- **One Rating Per User**: Each user can rate a product once (can be updated)
- **Average Calculation**: Automatic computation of average ratings from all reviews
- **Marketplace Display**: Star ratings shown on product cards with average and review count
- **Product Detail**: Full rating breakdown on product pages with individual reviews
- **Cascade Deletion**: Removing a review automatically updates product rating

### Developer Details
- **Endpoints**: Rating submission integrated with `/add_product_comment/<product_id>`
- **Rating Parameter**: Optional 'rating' field (integer 1-5) in comment form
- **Database**: ProductReview table with unique constraint per user-product pair
- **Frontend**: Pure JavaScript/CSS implementation with SVG star icons

## 🤖 AI Features

### Content Generation
- **Title Suggestions**: AI generates 3 varied engaging titles based on artwork analysis
- **Description Writing**: Contextual descriptions highlighting artistic elements
- **Style Adaptation**: Different suggestions for posts vs. products
- **Image Analysis**: AI analyzes uploaded images to understand content and context
- **Portfolio Narratives**: AI creates compelling stories connecting an artist's works

### Business Intelligence & Analytics
- **AI Insights Dashboard**: Comprehensive analytics powered by Groq's Llama 3.3 70B model
  - **Product Optimization**: Analysis of titles, descriptions, images, and hashtag usage
  - **Marketing Strategy**: Recommendations for improving visibility and engagement
  - **Pricing Strategy**: Data-driven pricing recommendations based on market analysis
  - **Growth Opportunities**: Identification of new markets, trends, and expansion possibilities
  
- **Competitive Pricing Analysis**: AI-powered market intelligence
  - **Smart Similarity Matching**: AI compares products based on characteristics, not just price
  - **Market Benchmarking**: Compare your pricing against similar products in the marketplace
  - **External Market Research**: Optional integration with Amazon, Etsy, and Flipkart pricing data
  - **Similarity Scoring**: AI provides percentage match scores and detailed reasoning
  - **Positioning Advice**: Get recommendations on whether your pricing is competitive, premium, or budget
  - **Price Difference Analysis**: Visual indicators showing how your prices compare to competitors

- **Analytics Dashboard Features**:
  - **Key Performance Indicators**: Views, Engagement, Items Sold, Revenue
  - **Trend Visualization**: 30-day charts for views and revenue
  - **Top Products**: Rankings by views and sales performance
  - **Category Analysis**: Sales breakdown by product category (hashtags)
  - **Engagement Metrics**: Top posts by likes and comments

### Translation Support
- **Multi-language**: Support for 15+ languages including Indian languages
- **SEO Optimization**: Translated content includes SEO phrases for better discoverability
- **Cultural Adaptation**: Translations consider cultural context
- **Language Detection**: Automatic detection of source language using Unicode ranges
- **Fallback Support**: Graceful degradation when AI services are unavailable

### Supported Languages
- **Indian Languages**: Hindi, Bengali, Tamil, Telugu, Marathi, Gujarati, Kannada, Malayalam, Punjabi, Urdu
- **International**: English, Spanish, French, German, Chinese, Japanese, Korean, Russian, Greek, Hebrew, Arabic
- **Script Support**: Devanagari, Bengali, Gurmukhi, Gujarati, Tamil, Telugu, Kannada, Malayalam, Arabic, CJK, Cyrillic, Greek, Hebrew

## 🎨 User Interface

### Design Philosophy
- **Clean & Modern**: Instagram-inspired interface
- **Mobile-First**: Responsive design for all devices
- **Accessibility**: Text-to-speech and keyboard navigation
- **Performance**: Optimized loading and smooth animations

### Key UI Components
- **Navigation**: Sticky header with search functionality
- **Cards**: Consistent card-based layout for posts and products
- **Forms**: Intuitive forms with real-time validation
- **Modals**: Smooth overlay interactions
- **Grid Layouts**: Responsive grid systems


## 🔒 Security Features

- **Password Hashing**: Secure password storage using Werkzeug
- **Session Management**: Flask-Login for secure sessions
- **File Upload Security**: Secure filename handling and type validation
- **Input Validation**: Server-side validation for all inputs
- **CSRF Protection**: Built-in CSRF protection with Flask

## 📊 Database Schema

### Users Table
- `id`: Primary key (auto-increment)
- `name`: User's display name (String, 100 chars)
- `email`: Unique email address (String, 100 chars)
- `password_hash`: Hashed password using Werkzeug (String, 255 chars)
- `phone`: Contact number (String, 20 chars)
- `location`: User's location (String, 150 chars)
- `created_at`: Account creation date (String, 250 chars)
- **Relationships**: One-to-many with Posts and Products

### Posts Table
- `post_id`: Primary key (auto-increment)
- `artist_id`: Foreign key to users.id
- `post_title`: Post title (String, 255 chars)
- `description`: Post description (Text)
- `media_url`: Image URL or path (String, 255 chars)
- `created_at`: Post creation date (String, 255 chars)
- `is_promoted`: Whether this post is a promoted product (Boolean)
- **Relationships**: Many-to-one with User

### Comments Table
- `comment_id`: Primary key (auto-increment)
- `post_id`: Foreign key to posts.post_id (CASCADE on delete)
- `user_id`: Foreign key to users.id
- `content`: Comment text (Text)
- `created_at`: Comment creation date (String, 250 chars)

### Post Likes Table
- `id`: Primary key (auto-increment)
- `post_id`: Foreign key to posts.post_id (CASCADE on delete)
- `user_id`: Foreign key to users.id

### Products Table
- `product_id`: Primary key (auto-increment)
- `artist_id`: Foreign key to users.id
- `title`: Product name (String, 150 chars)
- `description`: Product description (Text)
- `price`: Product price (Numeric, 10 digits, 2 decimal places)
- `img_url`: Product image URL or path (String, 255 chars)
- `created_at`: Product creation date (String, 250 chars)
- `is_promoted`: Promotion flag for product (Boolean) — currently used to track promotion state
- **Relationships**: Many-to-one with User

### ProductComments Table
- `comment_id`: Primary key (auto-increment)
- `product_id`: Foreign key to products.product_id (CASCADE on delete)
- `user_id`: Foreign key to users.id
- `content`: Comment/review text (Text)
- `created_at`: Comment creation date (String, 250 chars)

### ProductReview Table
- `review_id`: Primary key (auto-increment)
- `product_id`: Foreign key to products.product_id (CASCADE on delete)
- `user_id`: Foreign key to users.id
- `rating`: Star rating (Integer, 1-5)
- `title`: Optional review title (String, 255 chars)
- `content`: Optional review content (Text)
- `created_at`: Review creation date (String, 250 chars)
- `updated_at`: Review updated date (String, 250 chars)
- **Constraints**: One review per user per product (unique constraint on product_id + user_id)

### Cart Table
- `cart_id`: Primary key (auto-increment)
- `user_id`: Foreign key to users.id
- `product_id`: Foreign key to products.product_id
- `quantity`: Number of items (Integer, default 1)
- `added_at`: Date item added to cart (String, 250 chars)

### Orders Table
- `order_id`: Primary key (auto-increment)
- `user_id`: Foreign key to users.id (buyer)
- `product_id`: Foreign key to products.product_id
- `quantity`: Number of items ordered (Integer)
- `total_price`: Total order price (Numeric, 10 digits, 2 decimal places)
- `status`: Order status (String, 50 chars) - e.g., "pending", "completed", "cancelled"
- `created_at`: Order creation date (String, 250 chars)

### Hashtags Table
- `id`: Primary key (auto-increment)
- `name`: Hashtag name without # symbol (String, 100 chars, unique)
- `created_at`: Hashtag creation date (String, 250 chars)

### ProductHashtag Table
- `id`: Primary key (auto-increment)
- `product_id`: Foreign key to products.product_id (CASCADE on delete)
- `hashtag_id`: Foreign key to hashtags.id (CASCADE on delete)
- **Constraints**: Unique constraint on (product_id, hashtag_id)

### PostHashtag Table
- `id`: Primary key (auto-increment)
- `post_id`: Foreign key to posts.post_id (CASCADE on delete)
- `hashtag_id`: Foreign key to hashtags.id (CASCADE on delete)
- **Constraints**: Unique constraint on (post_id, hashtag_id)

### ProductView Table
- `id`: Primary key (auto-increment)
- `product_id`: Foreign key to products.product_id (CASCADE on delete)
- `artist_id`: Foreign key to users.id
- `created_at`: View timestamp (String, 250 chars)

### ProfileView Table
- `id`: Primary key (auto-increment)
- `profile_user_id`: Foreign key to users.id (CASCADE on delete)
- `created_at`: View timestamp (String, 250 chars)


### Environment Setup
```bash
export FLASK_ENV=production
export GEMINI_API_KEY=your_production_key
export FLASK_SECRET_KEY=your_production_secret
export GROQ_API_KEY=your_production_key
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.


## 🔮 Future Enhancements

- **Advanced AI**: More sophisticated content generation, image analysis and smart price assist for artisans
- **Advanced Search**: Recommendation system based on browsing history and preferences
- **Payment Integration**: Secure payment gateway integration for online transactions
- **Enhanced Analytics**: 
  - Conversion rate tracking (view-to-purchase)
  - Customer lifetime value analysis
  - Geographic insights and heat maps
  - Trend prediction and forecasting
  - Automated alerts for business opportunities
- **Review Moderation**: Tools for artists to respond to reviews and flag inappropriate content
- **AI Model Improvements**:
  - Fine-tuned models for better product similarity matching
  - Seasonal trend analysis and predictions
  - Automated inventory recommendations
  - Dynamic pricing suggestions based on demand


---

**Clyst** - Where Art Meets Community and Commerce
