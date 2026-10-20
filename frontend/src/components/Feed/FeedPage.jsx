import { useState, useEffect } from 'react';
import { postsAPI } from '../../api/api';
import PostCard from './PostCard';
import CreatePost from './CreatePost';

export default function FeedPage() {
    const [posts, setPosts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all');

    const loadPosts = async () => {
        try {
            const data = await postsAPI.getPosts();
            setPosts(data);
        } catch (error) {
            console.error('Error loading posts:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadPosts();
    }, []);

    const filteredPosts = filter === 'all'
        ? posts
        : posts.filter(post => post.category === filter);

    return (
        <div className="container" style={{ marginTop: '2rem', marginBottom: '2rem' }}>
            <div className="feed-header">
                <h2>Лента постов</h2>
                <div className="category-filters">
                    <button
                        className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
                        onClick={() => setFilter('all')}
                    >
                        Все
                    </button>
                    <button
                        className={`filter-btn ${filter === 'maintenance' ? 'active' : ''}`}
                        onClick={() => setFilter('maintenance')}
                    >
                        обслуживание
                    </button>
                    <button
                        className={`filter-btn ${filter === 'upgrade' ? 'active' : ''}`}
                        onClick={() => setFilter('upgrade')}
                    >
                        апгрейд
                    </button>
                    <button
                        className={`filter-btn ${filter === 'route' ? 'active' : ''}`}
                        onClick={() => setFilter('route')}
                    >
                        маршрут
                    </button>
                    <button
                        className={`filter-btn ${filter === 'tricks' ? 'active' : ''}`}
                        onClick={() => setFilter('tricks')}
                    >
                        трюки
                    </button>
                </div>
            </div>

            <CreatePost onPostCreated={loadPosts} />

            <div className="feed-content">
                {loading ? (
                    <div className="loading">Загрузка...</div>
                ) : filteredPosts.length === 0 ? (
                    <p className="empty-state">
                        {filter === 'all' ? 'Пока нет постов. Создайте первый!' : 'Нет постов в этой категории.'}
                    </p>
                ) : (
                    filteredPosts.map(post => <PostCard key={post.id} post={post} />)
                )}
            </div>
        </div>
    );
}
