import { useState } from 'react';
import { adminApi } from '../services/api';
import type { ModerationRole, PublicProfile } from '../types';
import AvatarImage from './common/AvatarImage';
import ModerationDialog from './common/ModerationDialog';

const ROLE_LABELS: Record<ModerationRole, string> = {
  user: 'Пользователь',
  moderator: 'Модератор',
};

export default function ManageUserRole({ profile }: { profile: PublicProfile }) {
  const [open, setOpen] = useState(false);
  const [selection, setSelection] = useState<ModerationRole>();
  const [saved, setSaved] = useState<ModerationRole>();

  return <div className="role-management">
    <button type="button" className="velo-button secondary" aria-haspopup="dialog" onClick={() => {
      setSelection(undefined);
      setOpen(true);
    }}>Управление ролью</button>
    {saved && <p role="status">Назначена роль: {ROLE_LABELS[saved]}</p>}
    {open && <ModerationDialog title="Управление ролью" confirm="Сохранить" disabled={!selection}
      onSubmit={async () => {
        if (!selection) return;
        const result = await adminApi.setRole(profile.id, selection);
        setSaved(result.role);
      }} onSuccess={() => setOpen(false)} onClose={() => setOpen(false)}>
      <div className="role-target">
        <div className="avatar"><AvatarImage username={profile.username} url={profile.avatar_url} /></div>
        <strong>{profile.username}</strong>
      </div>
      <div className="role-options" role="radiogroup" aria-label="Новая роль">
        {(['user', 'moderator'] as const).map(role => <label key={role}>
          <input type="radio" name="new-role" value={role} checked={selection === role}
            onChange={() => setSelection(role)} />
          {ROLE_LABELS[role]}
        </label>)}
      </div>
    </ModerationDialog>}
  </div>;
}
