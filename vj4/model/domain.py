from pymongo import errors

from vj4 import db
from vj4 import error
from vj4.model import builtin
from vj4.util import argmethod


@argmethod.wrap
async def add(domain_id: str, owner_uid: int,
              roles={builtin.ROLE_DEFAULT: builtin.DEFAULT_PERMISSIONS}):
  for domain in builtin.DOMAINS:
    if domain['_id'] == domain_id:
      raise error.DomainAlreadyExistError(domain_id)
  coll = db.Collection('domain')
  # TODO(twd2): Do we need to check owner's priv, quota, etc here?
  try:
    return await coll.insert({'_id': domain_id, 'owner_uid': owner_uid, 'roles': roles})
  except errors.DuplicateKeyError:
    raise error.DomainAlreadyExistError(domain_id) from None


@argmethod.wrap
async def get(domain_id: str, fields=None):
  for domain in builtin.DOMAINS:
    if domain['_id'] == domain_id:
      return domain
  coll = db.Collection('domain')
  return await coll.find_one(domain_id, fields)


def get_multi(fields=None):
  coll = db.Collection('domain')
  return coll.find({}, fields)


@argmethod.wrap
async def transfer(domain_id: str, old_owner_uid: int, new_owner_uid: int):
  for domain in builtin.DOMAINS:
    if domain['_id'] == domain_id:
      return None
  coll = db.Collection('domain')
  # TODO(twd2): Do we need to check new owner's priv, quota, etc here?
  return await coll.find_and_modify(query={'_id': domain_id, 'owner_uid': old_owner_uid},
                                    update={'$set': {'owner_uid': new_owner_uid}},
                                    new=True)


@argmethod.wrap
async def get_user(domain_id: str, uid: int, fields=None):
  coll = db.Collection('domain.user')
  return await coll.find_one({'domain_id': domain_id, 'uid': uid}, fields)


async def set_user(domain_id, uid, **kwargs):
  coll = db.Collection('domain.user')
  return await coll.find_and_modify(query={'domain_id': domain_id, 'uid': uid},
                                    update={'$set': kwargs},
                                    upsert=True,
                                    new=True)


async def inc_user(domain_id, uid, **kwargs):
  coll = db.Collection('domain.user')
  return await coll.find_and_modify(query={'domain_id': domain_id, 'uid': uid},
                                    update={'$inc': kwargs},
                                    upsert=True,
                                    new=True)


async def update_udocs(domain_id, udocs, fields=None):
  uids = set(udoc['_id'] for udoc in udocs)
  if uids:
    if fields:
      fields.update({'_id': 0, 'domain_id': 0})
    else:
      fields = {'_id': 0, 'domain_id': 0}
    coll = db.Collection('domain.user')
    uddocs = await (coll.find({'domain_id': domain_id, 'uid': {'$in': list(uids)}},
                              fields)
                    .to_list(None))
    uids = dict((uddoc['uid'], uddoc) for uddoc in uddocs)
    for udoc in udocs:
      if udoc['_id'] in uids:
        udoc.update(uids[udoc['_id']])
  return udocs


def get_multi_users(domain_id: str, fields=None):
  coll = db.Collection('domain.user')
  return coll.find({'domain_id': domain_id}, fields)


@argmethod.wrap
async def ensure_indexes():
  coll = db.Collection('domain')
  await coll.ensure_index('owner_uid')
  user_coll = db.Collection('domain.user')
  await user_coll.ensure_index([('domain_id', 1),
                                ('uid', 1)])
  await user_coll.ensure_index([('domain_id', 1),
                                ('rp', -1)])
  await user_coll.ensure_index([('domain_id', 1),
                                ('rank', 1)])


if __name__ == '__main__':
  argmethod.invoke_by_args()
