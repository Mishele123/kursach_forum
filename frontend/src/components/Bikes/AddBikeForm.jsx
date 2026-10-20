import { useState } from 'react';
import { bikesAPI } from '../../api/api';

export default function AddBikeForm({ onBikeAdded }) {
    const [brand, setBrand] = useState('');
    const [model, setModel] = useState('');
    const [year, setYear] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            await bikesAPI.addBike({
                brand,
                model,
                year: parseInt(year)
            });
            setBrand('');
            setModel('');
            setYear('');
            onBikeAdded();
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="create-post-section" style={{ marginTop: '2rem' }}>
            <h3>Добавить велосипед</h3>
            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label htmlFor="brand">Бренд</label>
                    <input
                        type="text"
                        id="brand"
                        value={brand}
                        onChange={(e) => setBrand(e.target.value)}
                        required
                        maxLength={100}
                        placeholder="Trek, Specialized..."
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="model">Модель</label>
                    <input
                        type="text"
                        id="model"
                        value={model}
                        onChange={(e) => setModel(e.target.value)}
                        required
                        maxLength={100}
                        placeholder="Fuel EX 9.8"
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="year">Год выпуска</label>
                    <input
                        type="number"
                        id="year"
                        value={year}
                        onChange={(e) => setYear(e.target.value)}
                        required
                        min="1800"
                        max="2026"
                        placeholder="2024"
                    />
                </div>
                {error && <p style={{ color: 'red' }}>{error}</p>}
                <button type="submit" className="btn btn-primary" disabled={loading}>
                    {loading ? 'Добавление...' : 'Добавить'}
                </button>
            </form>
        </div>
    );
}
