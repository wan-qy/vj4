import { AutoloadPage } from '../../misc/PageLoader';
import CmEditor from './cmeditor';
import delay from '../../utils/delay';

function runSubstitute($container) {
  const selector = ['textarea[data-markdown]'];
  $container.find(selector.join(', ')).each((i, element) => {
    CmEditor.getOrConstruct($(element));
  });
}

const cmEditorPage = new AutoloadPage(() => {
  runSubstitute($('body'));
  $(document).on('vjContentNew', async e => {
    await delay(0);
    runSubstitute($(e.target));
  });
});

export default cmEditorPage;
