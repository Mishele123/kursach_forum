import { NavLink, Link } from 'react-router-dom';
import { POST_CATEGORIES, CATEGORY_LABELS } from '../../utils/constants';
export default function Sidebar() {
  return <aside className="velo-sidebar"><p className="eyebrow">ВАШЕ ПРОСТРАНСТВО</p>
    <nav>{[['/feed','Лента'],['/profile','Мой профиль'],['/bikes','Мои велосипеды']].map(([path,label]) => <NavLink key={path} to={path}>{label}</NavLink>)}</nav>
    <hr/><p className="eyebrow">ТЕМЫ ДЛЯ ВДОХНОВЕНИЯ</p><div className="topic-links">{POST_CATEGORIES.map(c => <Link key={c} to={'/feed?category='+encodeURIComponent(c)}>{CATEGORY_LABELS[c]}</Link>)}</div>
    <div className="sidebar-cta"><h2>Всё начинается<br/>с велосипеда.</h2><p>Добавьте свой байк и найдите владельцев похожих моделей.</p><Link to="/bikes/add">Добавить велосипед</Link></div>
  </aside>;
}
