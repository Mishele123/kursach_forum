import { useState, useEffect } from 'react';
import { profileAPI, bikesAPI } from '../../api/api';
import BikesList from '../Bikes/BikesList';
import AddBikeForm from '../Bikes/AddBikeForm';

export default function ProfilePage({ user }) {
    const [profile, setProfile] = useState(null);
    const [bikes, setBikes] = useState([]);
    const [loading, setLoading] = useState(true);

    const loadProfile = async () => {
        try {
            const data = await profileAPI.getProfile();
            setProfile(data);
        } catch (error) {
            console.error('Error loading profile:', error);
        }
    };

    const loadBikes = async () => {
        try {
            const data = await bikesAPI.getBikes();
            setBikes(data);
        } catch (error) {
            console.error('Error loading bikes:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadProfile();
        loadBikes();
    }, []);

    if (loading) {
        return <div className="container loading" style={{ marginTop: '2rem' }}>Загрузка...</div>;
    }

    return (
        <div className="container" style={{ marginTop: '2rem', marginBottom: '2rem' }}>
            <div className="profile-header">
                <div className="profile-avatar">
                    {profile?.avatar_url ? (
                        <img src={profile.avatar_url} alt={profile.username} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                    ) : (
                        <div className="avatar-placeholder">
                            {user?.username?.charAt(0).toUpperCase()}
                        </div>
                    )}
                </div>
                <div className="profile-info">
                    <h2>{user?.username}</h2>
                    <p>{profile?.bio || 'Нет описания'}</p>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '0.5rem' }}>
                        {profile?.location || 'Местоположение не указано'}
                    </p>
                </div>
            </div>

            <BikesList bikes={bikes} />
            <AddBikeForm onBikeAdded={loadBikes} />
        </div>
    );
}
