export default function BikesList({ bikes }) {
    const formatDate = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('ru-RU', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    };

    if (bikes.length === 0) {
        return <p className="empty-state">У вас пока нет велосипедов</p>;
    }

    return (
        <div>
            <h3 style={{ fontFamily: 'var(--font-heading)', color: 'var(--ruby-ink)', marginBottom: '1rem' }}>
                Мои велосипеды
            </h3>
            <div className="bikes-grid">
                {bikes.map(bike => (
                    <div key={bike.id} className="bike-card">
                        <h4>{bike.brand} {bike.model}</h4>
                        <p><strong>Год:</strong> {bike.year}</p>
                        <p style={{ marginTop: '1rem', paddingTop: '0.75rem', borderTop: '1px solid var(--border-color)', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                            Добавлен: {formatDate(bike.created_at)}
                        </p>
                    </div>
                ))}
            </div>
        </div>
    );
}
