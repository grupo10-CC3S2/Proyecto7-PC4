echo "Instalando hooks"

cp hooks/commit-msg .git/hooks/
cp hooks/pre-commit .git/hooks/
cp hooks/pre-push .git/hooks/

chmod +x .git/hooks/commit-msg
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/pre-push

echo "Hooks instalados correctamente"
echo ""

