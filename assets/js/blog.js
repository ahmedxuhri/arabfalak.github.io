const POSTS_PER_PAGE = 10;
let allPosts = [];
let currentIndex = 0;
let isLoading = false;

async function loadPostsData() {
  try {
    const response = await fetch('/data/siteurls.json');
    allPosts = await response.json();
    
    // Sort posts by date (most recent first)
    allPosts.sort((a, b) => new Date(b.date_published) - new Date(a.date_published));
    
    return true;
  } catch (error) {
    console.error('Error loading posts data:', error);
    document.getElementById('posts-container').innerHTML = '<p>حدث خطأ في تحميل المقالات.</p>';
    return false;
  }
}

function createPostElement(post) {
  const date = new Date(post.date_published);
  const formattedDate = date.toLocaleDateString('ar-SA', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  });

  const article = document.createElement('article');
  article.className = 'post-card';
  article.innerHTML = `
    <span class="post-category">${post.category}</span>
    <h3><a href="${post.url}" style="text-decoration: none; color: inherit;">${post.title}</a></h3>
    <time>${formattedDate}</time>
    <p class="excerpt">${post.excerpt}</p>
    <a href="${post.url}" class="read-more">اقرأ المزيد →</a>
  `;
  
  return article;
}

function loadMorePosts() {
  if (isLoading || currentIndex >= allPosts.length) return;
  
  isLoading = true;
  const container = document.getElementById('posts-container');
  const endIndex = Math.min(currentIndex + POSTS_PER_PAGE, allPosts.length);
  
  for (let i = currentIndex; i < endIndex; i++) {
    container.appendChild(createPostElement(allPosts[i]));
  }
  
  currentIndex = endIndex;
  isLoading = false;
}

function setupInfiniteScroll() {
  // Create a sentinel element at the bottom
  const sentinel = document.createElement('div');
  sentinel.id = 'scroll-sentinel';
  sentinel.style.height = '50px';
  document.getElementById('posts-container').parentElement.appendChild(sentinel);
  
  // Use Intersection Observer to detect when user scrolls near the bottom
  const observer = new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting && currentIndex < allPosts.length) {
      loadMorePosts();
    }
  }, {
    rootMargin: '200px' // Trigger 200px before reaching the sentinel
  });
  
  observer.observe(sentinel);
}

async function initBlog() {
  const success = await loadPostsData();
  if (success) {
    loadMorePosts(); // Load initial batch
    setupInfiniteScroll(); // Setup scroll observer
  }
}

// Initialize when the DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initBlog);
} else {
  initBlog();
}
