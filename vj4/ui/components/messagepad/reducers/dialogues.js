import _ from 'lodash';

export default function reducer(state = {}, action) {
  switch (action.type) {
  case 'DIALOGUES_LOAD_DIALOGUES_FULFILLED': {
    return _.keyBy(action.payload.messages, '_id');
  }
  case 'DIALOGUES_CREATE': {
    const { id, uid } = action.payload;
    return {
      ...state,
      [id]: {
        _id: id,
        sender_uid: UserContext.uid,
        sendee_uid: uid,
        sendee_udoc: {
          uname: `UID = ${String(uid)}`,
        },
        reply: [],
        isPlaceholder: true,
      },
    };
  }
  case 'DIALOGUES_POST_REPLY_FULFILLED': {
    const id = action.meta.dialogueId;
    const { reply } = action.payload;
    return {
      ...state,
      [id]: {
        ...state[id],
        reply: [
          ...state[id].reply,
          reply,
        ],
      },
    };
  }
  case 'DIALOGUES_POST_SEND_FULFILLED': {
    const { placeholderId } = action.meta;
    return {
      ..._.omit(state, placeholderId),
      [action.payload.mdoc._id]: action.payload.mdoc,
    };
  }
  case 'DIALOGUES_MESSAGE_PUSH': {
    const { type, data } = action.payload;
    const id = data._id;
    if (type === 'new') {
      return {
        ...state,
        [id]: data,
      };
    } else if (type === 'reply') {
      if (state[id] === undefined) {
        window.location.reload();
        return state;
      }
      return {
        ...state,
        [id]: {
          ...state[id],
          reply: [
            ...state[id].reply,
            data.reply[0],
          ],
        },
      };
    }
    return state;
  }
  default:
    return state;
  }
}
